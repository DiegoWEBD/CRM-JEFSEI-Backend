from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from app.dominio.auth.sesion import Sesion


class AuthenticationService(ABC):

    # ── Contraseña ──────────────────────────────────────────────

    @abstractmethod
    def hash_password(self, password: str) -> str:
        pass

    @abstractmethod
    def verificar_password(self, password_texto_plano: str, password_encriptada: str) -> bool:
        pass

    # ── JWT (bajo nivel) ────────────────────────────────────────

    @abstractmethod
    def crear_access_token(self, data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    def decodificar_token(self, token: str) -> dict[str, Any] | None:
        pass

    # ── Sesiones y refresh tokens ───────────────────────────────

    @abstractmethod
    def crear_sesion_y_tokens(
        self,
        claims: dict[str, Any],
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[str, str]:
        """Crea una sesión, genera access token (JWT) y refresh token (opaco).

        Retorna (access_token, refresh_token).
        """
        pass

    @abstractmethod
    def rotar_tokens(self, refresh_token_plano: str) -> tuple[str, str]:
        """Valida el refresh token, lo rota y emite un nuevo par.

        Retorna (nuevo_access_token, nuevo_refresh_token).

        Raises:
            RefreshTokenInvalidoError: token inválido o expirado.
            RefreshTokenReusadoError: token ya usado (familia revocada).
        """
        pass

    @abstractmethod
    def revocar_sesion(self, sesion_id: UUID, motivo: str) -> None:
        pass

    @abstractmethod
    def revocar_todas_las_sesiones(self, rut: str, motivo: str) -> None:
        pass

    @abstractmethod
    def obtener_sesion_viva(self, sesion_id: UUID) -> Sesion | None:
        pass
