from datetime import datetime, timezone

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.aplicacion.notificacion.use_cases.generar_alerta_renovacion_poliza import GenerarAlertaRenovacionPolizaUseCase
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.historial_estado.historial_estado_proceso_comercial import HistorialEstadoProcesoComercial
from app.dominio.historial_estado.repositorio_historial_estado_procesos_comerciales import RepositorioHistorialEstadoProcesosComerciales
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.usuario import Usuario


class DescartarProcesoComercialUseCase:

    def __init__(
        self,
        authorization_service: AuthorizationService,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_prospectos: RepositorioProspectos,
        repositorio_historial: RepositorioHistorialEstadoProcesosComerciales,
        repositorio_notificaciones: RepositorioNotificaciones,
        servicio_alertas: ServicioAlertasProceso,
    ):
        self.authorization_service = authorization_service
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_historial = repositorio_historial
        self.repositorio_notificaciones = repositorio_notificaciones
        self.servicio_alertas = servicio_alertas

    def ejecutar(self, id: int, observacion: str | None, usuario: Usuario):
        proceso = self.repositorio_procesos_comerciales.buscar(id)

        if not proceso:
            raise RecursoNoEncontradoException(f'No se encontró la oportunidad comercial {id}')

        if proceso.cerrado:
            raise ConflictoEnAccionException('Solo se puede descartar una oportunidad abierta')

        prospecto = self.repositorio_prospectos.buscar(proceso.id_prospecto)

        if not prospecto:
            raise RecursoNoEncontradoException(f'No se encontró el prospecto {proceso.id_prospecto}')

        if not self.authorization_service.usuario_puede_descartar_proceso_comercial(prospecto, usuario):
            raise UsuarioNoAutorizadoException(
                'Solo el ejecutivo comercial asignado puede descartar la oportunidad'
            )

        ahora = datetime.now(tz=timezone.utc)
        proceso.descartado = True
        proceso.cerrado = True
        proceso.fecha_cierre = ahora
        proceso.motivo_cierre = observacion
        self.repositorio_procesos_comerciales.actualizar(proceso)

        self.repositorio_historial.registrar(
            HistorialEstadoProcesoComercial(
                id_proceso_comercial=id,
                codigo_estado='OPORTUNIDAD_DESCARTADA',
                rut_registrado_por=usuario.rut,
                fecha=ahora,
                observacion=observacion,
            )
        )

        # Al descartar la oportunidad, todas sus alertas dejan de ser
        # relevantes: se marcan leídas con la misma fecha del descarte.
        destinatarios = self.servicio_alertas.marcar_todas_leidas(id, ahora)

        if destinatarios:
            hub.publicar_desde_hilo(
                destinatarios,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_leidas_descarte'},
            )
