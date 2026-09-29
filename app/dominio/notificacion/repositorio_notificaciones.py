from abc import ABC, abstractmethod

from app.dominio.notificacion.notificacion import Notificacion
from app.dominio.notificacion.proceso_alertable_sla import ProcesoAlertableSla


class RepositorioNotificaciones(ABC):

    @abstractmethod
    def obtener_procesos_alertables(self) -> list[ProcesoAlertableSla]:
        pass

    @abstractmethod
    def registrar(self, notificacion: Notificacion) -> bool:
        """Inserta la notificación. Retorna False si su dedupe_key ya existía."""
        pass

    @abstractmethod
    def obtener_paginado(
        self,
        rut_usuario: str,
        no_leidas: bool | None,
        nivel: str | None,
        codigo_tipo: str | None,
        pagina: int,
        tamano_pagina: int,
    ) -> tuple[list[Notificacion], int]:
        pass

    @abstractmethod
    def obtener_contador_no_leidas(self, rut_usuario: str) -> int:
        pass

    @abstractmethod
    def marcar_leida(self, id_notificacion: int, rut_usuario: str) -> None:
        pass

    @abstractmethod
    def marcar_todas_leidas(self, rut_usuario: str) -> int:
        """Marca todas las no leídas del usuario. Retorna el total marcado."""
        pass
