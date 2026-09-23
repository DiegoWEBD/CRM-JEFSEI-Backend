from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones


class ObtenerContadorNoLeidasUseCase:

    def __init__(self, repositorio_notificaciones: RepositorioNotificaciones) -> None:
        self.repositorio_notificaciones = repositorio_notificaciones

    def ejecutar(self, rut_usuario: str) -> int:
        return self.repositorio_notificaciones.obtener_contador_no_leidas(
            rut_usuario=rut_usuario
        )
