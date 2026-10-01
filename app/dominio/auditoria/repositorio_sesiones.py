from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from psycopg import Connection
from psycopg.rows import DictRow

from app.dominio.auditoria.sesion import Sesion


class TokenRotadoInvalido(Exception):
    """El refresh token presentado no sirve.

    ``motivo`` distingue un token vencido de uno ya usado fuera de la ventana de
    gracia, porque lo segundo es señal de robo y revoca la sesión completa.
    """

    def __init__(self, motivo: str, revocar_sesion: bool = False):
        super().__init__(motivo)
        self.motivo = motivo
        self.revocar_sesion = revocar_sesion


class RepositorioSesiones(ABC):

    @abstractmethod
    def crear(self, sesion: Sesion, conn: Optional[Connection[DictRow]] = None) -> Sesion:
        pass

    @abstractmethod
    def obtener_por_id(
        self,
        id_sesion: str,
        conn: Optional[Connection[DictRow]] = None,
    ) -> Sesion | None:
        pass

    @abstractmethod
    def revocar(
        self,
        id_sesion: str,
        motivo: str,
        conn: Optional[Connection[DictRow]] = None,
    ) -> None:
        pass

    @abstractmethod
    def revocar_todas_del_usuario(
        self,
        rut_usuario: str,
        motivo: str,
        conn: Optional[Connection[DictRow]] = None,
    ) -> int:
        pass

    @abstractmethod
    def registrar_uso(self, id_sesion: str, conn: Optional[Connection[DictRow]] = None) -> None:
        pass

    # --- Refresh tokens ---

    @abstractmethod
    def crear_refresh_token(
        self,
        id_sesion: str,
        token_hash: str,
        fecha_expiracion: datetime,
        conn: Optional[Connection[DictRow]] = None,
    ) -> str:
        pass

    @abstractmethod
    def obtener_refresh_token_por_hash(
        self,
        token_hash: str,
        conn: Optional[Connection[DictRow]] = None,
    ) -> dict | None:
        """Fila con id, id_sesion, fechas, revocado y usado."""
        pass

    @abstractmethod
    def marcar_refresh_token_usado(
        self,
        id_refresh_token: str,
        conn: Optional[Connection[DictRow]] = None,
    ) -> None:
        pass

    @abstractmethod
    def revocar_refresh_tokens_de_sesion(
        self,
        id_sesion: str,
        conn: Optional[Connection[DictRow]] = None,
    ) -> None:
        pass

    @abstractmethod
    def revocar_refresh_tokens_older_than(
        self,
        id_sesion: str,
        id_refresh_token: str,
        conn: Optional[Connection[DictRow]] = None,
    ) -> int:
        """Deja activo un único refresh token por sesión."""
        pass
