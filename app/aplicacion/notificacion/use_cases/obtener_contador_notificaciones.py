from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones


class ObtenerContadorNotificacionesUseCase:

    def __init__(self, repositorio_notificaciones: RepositorioNotificaciones) -> None:
        self.repositorio_notificaciones = repositorio_notificaciones

    def ejecutar(self, rut_usuario: str, leidas: bool, leibles: bool) -> int:
        return self.repositorio_notificaciones.contar(
            rut_usuario=rut_usuario,
            leidas=leidas,
            leibles=leibles
        )
