from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones


class MarcarNotificacionesLeidasUseCase:

    def __init__(self, repositorio_notificaciones: RepositorioNotificaciones) -> None:
        self.repositorio_notificaciones = repositorio_notificaciones

    def ejecutar(self, rut_usuario: str) -> int:
        return self.repositorio_notificaciones.marcar_todas_leidas(
            rut_usuario=rut_usuario
        )
