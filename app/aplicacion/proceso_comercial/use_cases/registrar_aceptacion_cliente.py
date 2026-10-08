from datetime import datetime, timezone

from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_SLA
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.usuario.usuario import Usuario


class RegistrarAceptacionClienteUseCase:

    def __init__(
        self,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_notificaciones: RepositorioNotificaciones,
        servicio_alertas: ServicioAlertasProceso
    ) -> None:
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.repositorio_notificaciones = repositorio_notificaciones
        self.servicio_alertas = servicio_alertas

    def ejecutar(self, id_proceso_comercial: int, usuario: Usuario):

        if not self.repositorio_procesos_comerciales.buscar(id_proceso_comercial):
            raise RecursoNoEncontradoException('Proceso comercial no encontrado')

        self.repositorio_procesos_comerciales.registrar_aceptacion_cliente(
            id=id_proceso_comercial,
            rut_usuario=usuario.rut
        )

        # La alerta de permanencia en el estado anterior deja de ser relevante.
        ahora = datetime.now(tz=timezone.utc)
        destinatarios = self.servicio_alertas.marcar_leidas(
            id_proceso_comercial, TIPOS_ALERTA_SLA, ahora
        )

        if destinatarios:
            hub.publicar_desde_hilo(
                destinatarios,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_leidas_cambio_estado'},
            )