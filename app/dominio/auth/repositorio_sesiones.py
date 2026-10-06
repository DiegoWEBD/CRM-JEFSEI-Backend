from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.dominio.auth.sesion import Sesion


class RepositorioSesiones(ABC):

    @abstractmethod
    def crear_sesion(
        self,
        rut_usuario: str,
        ip: str | None,
        user_agent: str | None,
        expira_en: datetime,
    ) -> UUID:
        """Crea una sesión y retorna su id."""
        pass

    @abstractmethod
    def guardar_refresh_token(
        self,
        sesion_id: UUID,
        token_hash: str,
        expira_en: datetime,
    ) -> UUID:
        """Persiste un refresh token (solo el hash). Retorna su id."""
        pass

    @abstractmethod
    def obtener_sesion_viva(self, sesion_id: UUID) -> Sesion | None:
        """Sesión activa (no revocada, no expirada) o None."""
        pass

    @abstractmethod
    def obtener_sesion_por_refresh_hash(
        self,
        token_hash: str,
    ) -> dict | None:
        """Busca la sesión y el token asociados al hash del refresh token.

        Retorna un dict con claves: sesion_id, token_id, token_usado_en,
        token_expira_en, sesion_revocado_en, sesion_expira_en — o None si no existe.
        """
        pass

    @abstractmethod
    def marcar_refresh_usado(
        self,
        token_id: UUID,
        nuevo_token_id: UUID,
    ) -> None:
        """Marca un refresh token como usado y enlaza su reemplazo."""
        pass

    @abstractmethod
    def actualizar_ultimo_acceso(self, sesion_id: UUID) -> None:
        """Actualiza el timestamp de último acceso de la sesión."""
        pass

    @abstractmethod
    def revocar_sesion(self, sesion_id: UUID, motivo: str) -> None:
        """Revoca una sesión individual."""
        pass

    @abstractmethod
    def revocar_sesiones_usuario(self, rut: str, motivo: str) -> None:
        """Revoca todas las sesiones activas de un usuario."""
        pass
