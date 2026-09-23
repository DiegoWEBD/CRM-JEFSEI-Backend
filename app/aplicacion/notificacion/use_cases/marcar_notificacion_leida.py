from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones


class MarcarNotificacionLeidaUseCase:

    def __init__(self, repositorio_notificaciones: RepositorioNotificaciones) -> None:
        self.repositorio_notificaciones = repositorio_notificaciones

    def ejecutar(self, id_notificacion: int, rut_usuario: str) -> None:
        self.repositorio_notificaciones.marcar_leida(
            id_notificacion=id_notificacion,
            rut_usuario=rut_usuario,
        )
