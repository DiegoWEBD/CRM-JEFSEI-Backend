from datetime import datetime, timezone

from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_SLA
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.usuario.usuario import Usuario


class CambiarEstadoManualUseCase:

    def __init__(
        self,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_notificaciones: RepositorioNotificaciones,
        servicio_alertas: ServicioAlertasProceso,
    ):
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.repositorio_notificaciones = repositorio_notificaciones
        self.servicio_alertas = servicio_alertas

    def ejecutar(
        self,
        id: int,
        codigo_estado_destino: str,
        observacion: str | None,
        usuario: Usuario,
    ):
        proceso = self.repositorio_procesos_comerciales.buscar(id)

        if not proceso:
            raise RecursoNoEncontradoException(f'No se encontró la oportunidad comercial {id}')

        if proceso.cerrado:
            raise ConflictoEnAccionException('La oportunidad está cerrada')

        if proceso.ejecutivo_comercial is None or usuario.rut != proceso.ejecutivo_comercial.rut:
            raise UsuarioNoAutorizadoException('Solo el ejecutivo comercial asignado puede cambiar el estado manualmente')

        self.repositorio_procesos_comerciales.cambiar_estado_manual(
            id=id,
            codigo_estado_destino=codigo_estado_destino,
            observacion=observacion,
            rut_usuario=usuario.rut,
        )

        # La alerta de permanencia en el estado anterior deja de ser relevante.
        ahora = datetime.now(tz=timezone.utc)
        destinatarios = self.servicio_alertas.marcar_leidas(id, TIPOS_ALERTA_SLA, ahora)

        if destinatarios:
            hub.publicar_desde_hilo(
                destinatarios,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_leidas_cambio_estado'},
            )
