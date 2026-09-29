from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones


class MarcarNotificacionLeidaUseCase:

    def __init__(self, repositorio_notificaciones: RepositorioNotificaciones) -> None:
        self.repositorio_notificaciones = repositorio_notificaciones

    def ejecutar(self, id_notificacion: int, rut_usuario: str) -> None:
        self.repositorio_notificaciones.marcar_leida(
            id_notificacion=id_notificacion,
            rut_usuario=rut_usuario,
        )

        # Avisa al resto de pestañas/sesiones del usuario. Si la notificación no
        # existe o es de otro usuario, el repositorio lanza y nunca llega aquí.
        hub.publicar_desde_hilo(
            [rut_usuario],
            {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'marcadas_leidas'},
        )
