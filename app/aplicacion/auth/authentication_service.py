from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from app.dominio.auth.sesion import Sesion
from app.dominio.usuario.usuario import Usuario


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
    def crear_access_token(self, usuario: Usuario, sid: str | None = None) -> str:
        """Firma el access token (JWT) a partir del usuario.

        Es el único punto donde se arman los claims de identidad
        (rut, nombre, codigo_roles, nombre_roles, codigo_permisos):
        login y refresh pasan por acá, así que siempre emiten los mismos.
        """
        pass

    @abstractmethod
    def decodificar_token(self, token: str) -> dict[str, Any] | None:
        pass

    # ── Sesiones y refresh tokens ───────────────────────────────

    @abstractmethod
    def crear_sesion_y_tokens(
        self,
        usuario: Usuario,
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[str, str]:
        """Crea una sesión, genera access token (JWT) y refresh token (opaco).

        Retorna (access_token, refresh_token).
        """
        pass

    @abstractmethod
    def rotar_refresh_token(self, refresh_token_plano: str) -> tuple[Sesion, str]:
        """Valida el refresh token y rota la familia.

        Retorna (sesion, nuevo_refresh_token). No emite el access token:
        quien lo arma es el caso de uso, con el usuario actualizado desde
        la base de datos (mismos claims que el login).

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
