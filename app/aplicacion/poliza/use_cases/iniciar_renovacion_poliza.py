from datetime import datetime, timezone

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.estado_informativo_proceso_comercial.repositorio_estados_proceso_comercial import RepositorioEstadosProcesoComercial
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.historial_estado.historial_estado_proceso_comercial import HistorialEstadoProcesoComercial
from app.dominio.historial_estado.repositorio_historial_estado_procesos_comerciales import RepositorioHistorialEstadoProcesosComerciales
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas
from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.usuario import Usuario


class IniciarRenovacionPolizaUseCase:

    def __init__(
        self,
        repositorio_prospectos: RepositorioProspectos,
        repositorio_polizas: RepositorioPolizas,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_estados: RepositorioEstadosProcesoComercial,
        repositorio_historial: RepositorioHistorialEstadoProcesosComerciales,
        authorization_service: AuthorizationService,
        servicio_alertas: ServicioAlertasProceso,
    ) -> None:
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_polizas = repositorio_polizas
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.authorization_service = authorization_service
        self.servicio_alertas = servicio_alertas
        self.repositorio_estados = repositorio_estados
        self.repositorio_historial = repositorio_historial

    def ejecutar(self, numero_poliza: str, usuario: Usuario) -> int:
        if not self.repositorio_polizas.buscar(numero_poliza):
            raise RecursoNoEncontradoException(f'Póliza {numero_poliza} no encontrada')

        if not self.authorization_service.usuario_puede_gestionar_renovacion(usuario.rut, numero_poliza):
            raise UsuarioNoAutorizadoException

        if self.repositorio_procesos_comerciales.buscar_renovacion_por_poliza_base(numero_poliza) is not None:
            raise ConflictoEnAccionException(
                f'La póliza {numero_poliza} ya tiene un proceso de renovación iniciado'
            )

        nuevo_estado = self.repositorio_estados.obtener_por_codigo('OPORTUNIDAD_CREADA')

        if not nuevo_estado:
            raise ConflictoEnAccionException('Error al crear proceso de renovación')

        id_proceso_comercial = self.repositorio_procesos_comerciales.nuevo_renovacion(
            numero_poliza, usuario.rut
        )

        if id_proceso_comercial is None:
            raise RecursoNoEncontradoException(f'Error al crear el proceso de renovación de la póliza {numero_poliza}')

        proceso = self.repositorio_procesos_comerciales.buscar(id_proceso_comercial)

        if not proceso:
            raise RecursoNoEncontradoException(f'Error al crear el proceso de renovación de la póliza {numero_poliza}')

        prospecto = self.repositorio_prospectos.buscar(proceso.id_prospecto)

        if not prospecto:
            raise RecursoNoEncontradoException(f'Error al crear el proceso de renovación de la póliza {numero_poliza}')

        ahora = datetime.now(tz=timezone.utc)

        # Al ser una oportunidad de renovación, sólo se asignan los ejecutivos de renovación y el asistente de renovación del prospecto
        proceso.ejecutivo_renovacion = prospecto.ejecutivo_renovacion_asignado
        proceso.asistente_renovacion = prospecto.asistente_renovacion_asignado
        proceso.estado_actual = nuevo_estado

        self.repositorio_procesos_comerciales.guardar(proceso, es_nuevo=False)

        self.repositorio_historial.registrar(HistorialEstadoProcesoComercial(
            id_proceso_comercial=proceso.id,
            codigo_estado=nuevo_estado.codigo,
            rut_registrado_por=usuario.rut,
            fecha=ahora
        ))

        destinatarios = self.servicio_alertas.marcar_leidas_renovacion(numero_poliza, ahora)

        if destinatarios:
            hub.publicar_desde_hilo(
                destinatarios,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_renovacion_resueltas'},
            )

        return id_proceso_comercial
