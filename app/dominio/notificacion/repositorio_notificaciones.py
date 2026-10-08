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
    def existe_alerta_proceso(self, codigo_tipo: str, id_proceso: int, rut_usuario: str) -> bool:
        """Indica si ya existe una alerta de ese tipo para el proceso y el RUT.

        Guarda anti-duplicado: la dedupe_key de las alertas de cierre incluye
        timestamp, por lo que el UNIQUE ya no evita duplicados entre corridas
        del scheduler.
        """
        pass

    @abstractmethod
    def buscar_notificaciones_proceso_comercial(self, id_proceso_comercial: int) -> list[Notificacion]:
        """Todas las notificaciones ligadas al proceso comercial (leídas o no)."""
        pass

    @abstractmethod
    def buscar_notificaciones_sla_por_rol(self, id_prospecto: int, rol: str) -> list[Notificacion]:
        """Alertas SLA no leídas de procesos abiertos del prospecto cuyo estado
        siguiente tenga `rol` como responsable."""
        pass

    @abstractmethod
    def actualizar(self, notificacion: Notificacion) -> None:
        """Actualiza todos los campos editables de la notificación por id.

        Es idempotente: si la notificación no cambió, no tiene ningún efecto
        observable. No toca `id` ni `created_at` (inmutables).
        """
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
    def obtener_ruts_por_roles(self, roles: list[str]) -> dict[str, list[str]]:
        """Devuelve {rol: [rut1, rut2, ...]} para los roles dados.

        Solo incluye usuarios habilitados y no eliminados.
        Se usa para el fan-out de alertas SLA a roles sin asignación
        por proceso (p.ej. GERENTE_COMERCIAL).
        """
        pass

    @abstractmethod
    def contar(self, rut_usuario: str, leidas: bool, leibles: bool) -> int:
        pass

    @abstractmethod
    def buscar(self, id_notificacion: int) -> Notificacion | None:
        """Busca una notificación por id. Retorna None si no existe."""
        pass

    @abstractmethod
    def marcar_leida(self, id_notificacion: int, rut_usuario: str) -> None:
        pass

    @abstractmethod
    def marcar_todas_leidas(self, rut_usuario: str) -> int:
        """Marca todas las no leíbles y no leídas del usuario. Retorna el total marcado."""
        pass
