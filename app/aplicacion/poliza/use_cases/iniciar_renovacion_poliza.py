from datetime import datetime, timezone

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.usuario import Usuario


class IniciarRenovacionPolizaUseCase:
    """Inicia el proceso comercial de renovación de una póliza.

    El proceso nace en OPORTUNIDAD_CREADA con el mismo prospecto y producto
    de la póliza base y queda enlazado vía ProcesoComercialRenovacion. Al
    iniciarlo, las alertas de renovación de la póliza quedan resueltas: sus
    hitos dejan de aplicar porque la renovación ya está en gestión.
    """

    def __init__(
        self,
        repositorio_prospectos: RepositorioProspectos,
        repositorio_polizas: RepositorioPolizas,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        authorization_service: AuthorizationService,
        servicio_alertas: ServicioAlertasProceso,
    ) -> None:
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_polizas = repositorio_polizas
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.authorization_service = authorization_service
        self.servicio_alertas = servicio_alertas

    def ejecutar(self, numero_poliza: str, usuario: Usuario) -> int:
        if not self.repositorio_polizas.buscar(numero_poliza):
            raise RecursoNoEncontradoException(f'Póliza {numero_poliza} no encontrada')

        if not self.authorization_service.usuario_puede_gestionar_renovacion(usuario.rut, numero_poliza):
            raise UsuarioNoAutorizadoException

        if self.repositorio_procesos_comerciales.buscar_renovacion_por_poliza_base(numero_poliza) is not None:
            raise ConflictoEnAccionException(
                f'La póliza {numero_poliza} ya tiene un proceso de renovación iniciado'
            )

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

        # Al ser una oportunidad de renovación, sólo se asignan los ejecutivos de renovación y el asistente de renovación del prospecto
        proceso.ejecutivo_renovacion = prospecto.ejecutivo_renovacion_asignado
        proceso.asistente_renovacion = prospecto.asistente_renovacion_asignado

        ahora = datetime.now(tz=timezone.utc)
        destinatarios = self.servicio_alertas.marcar_leidas_renovacion(numero_poliza, ahora)

        if destinatarios:
            hub.publicar_desde_hilo(
                destinatarios,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_renovacion_resueltas'},
            )

        return id_proceso_comercial
