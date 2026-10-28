from datetime import datetime

from app.dominio.notificacion.repositorio_notificaciones import (
    RepositorioNotificaciones,
)
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_RENOVACION


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

    """Marca leídas todas las alertas no leídas del proceso, sin importar su tipo.

    Se invoca al descartar la oportunidad: al dejar de estar activa, todas
    sus alertas dejan de ser relevantes. Devuelve los RUTs cuyas alertas
    fueron marcadas (alertas huérfanas sin destinatario quedan fuera), para
    que el caso de uso publique el refresco correspondiente por socket.
    """
    def marcar_todas_leidas(
        self,
        id_proceso_comercial: int,
        ahora: datetime,
    ) -> list[str]:
        destinatarios: list[str] = []

        for notificacion in self.repositorio_notificaciones.buscar_notificaciones_proceso_comercial(
            id_proceso_comercial
        ):
            if notificacion.leida:
                continue

            notificacion.leida = True
            notificacion.fecha_leida = ahora
            self.repositorio_notificaciones.actualizar(notificacion)

            if notificacion.rut_usuario:
                destinatarios.append(notificacion.rut_usuario)

        return destinatarios

    """Marca leídas las alertas de renovación no leídas de la póliza.

    Se invoca cuando los hitos dejan de aplicar: al cambiar el fin de
    vigencia de la póliza, al iniciar su proceso de renovación y al
    escalonar (un hito superior deja obsoletos a los anteriores). Con
    `tipos` se acota a esos tipos de alerta; por defecto, todas las de
    renovación. Devuelve los RUTs cuyas alertas fueron marcadas para
    publicar el refresco por socket.
    """
    def marcar_leidas_renovacion(
        self,
        numero_poliza: str,
        ahora: datetime,
        tipos: tuple[str, ...] = TIPOS_ALERTA_RENOVACION,
    ) -> list[str]:
        destinatarios: list[str] = []

        for notificacion in self.repositorio_notificaciones.buscar_notificaciones_por_poliza(
            numero_poliza
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
