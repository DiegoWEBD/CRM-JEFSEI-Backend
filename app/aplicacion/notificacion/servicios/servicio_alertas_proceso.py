from datetime import datetime

from app.dominio.notificacion.repositorio_notificaciones import (
    RepositorioNotificaciones,
)


class ServicioAlertasProceso:
    def __init__(self, repositorio_notificaciones: RepositorioNotificaciones) -> None:
        self.repositorio_notificaciones = repositorio_notificaciones


    """Marca leídas las alertas no leídas del proceso de los tipos dados.

    Devuelve los RUTs cuyas alertas fueron marcadas (alertas huérfanas sin
    destinatario quedan fuera), para que el caso de uso publique el
    refresco correspondiente por socket.
    """
    def marcar_leidas(
        self,
        id_proceso_comercial: int,
        tipos: tuple[str, ...],
        ahora: datetime,
    ) -> list[str]:
        destinatarios: list[str] = []

        for notificacion in self.repositorio_notificaciones.buscar_notificaciones_proceso_comercial(
            id_proceso_comercial
        ):
            if notificacion.codigo_tipo not in tipos:
                continue

            if notificacion.leida:
                continue

            notificacion.leida = True
            notificacion.fecha_leida = ahora
            self.repositorio_notificaciones.actualizar(notificacion)

            if notificacion.rut_usuario:
                destinatarios.append(notificacion.rut_usuario)

        return destinatarios
