import hashlib
import secrets
from typing import Any
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from passlib.context import CryptContext
import jwt
from jwt.exceptions import PyJWTError as JWTError

from app.aplicacion.auth.authentication_service import AuthenticationService
from app.core.config import settings
from app.dominio.auth.exceptions import RefreshTokenInvalidoError, RefreshTokenReusadoError
from app.dominio.auth.repositorio_sesiones import RepositorioSesiones
from app.dominio.auth.sesion import Sesion
from app.dominio.usuario.usuario import Usuario


class JwtAuthenticationService(AuthenticationService):

    def __init__(self, repositorio_sesiones: RepositorioSesiones | None = None):
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto"
        )
        self._sesiones = repositorio_sesiones

    # ── Contraseña ──────────────────────────────────────────────

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verificar_password(self, password_texto_plano: str, password_encriptada: str) -> bool:
        return self.pwd_context.verify(password_texto_plano, password_encriptada)

    # ── JWT (bajo nivel) ────────────────────────────────────────

    @staticmethod
    def _claims_de_usuario(usuario: Usuario) -> dict[str, Any]:
        """Claims de identidad compartidos por login y refresh."""
        return {
            "rut": usuario.rut,
            "nombre": usuario.nombre,
            "codigo_roles": [rol.codigo for rol in usuario.roles],
            "nombre_roles": [rol.nombre for rol in usuario.roles],
            "codigo_permisos": list(set(
                permiso.codigo
                for rol in usuario.roles
                for permiso in rol.permisos
            )),
        }

    def crear_access_token(self, usuario: Usuario, sid: str | None = None) -> str:
        to_encode = self._claims_de_usuario(usuario)
        if sid is not None:
            to_encode["sid"] = sid
        to_encode["jti"] = str(uuid4())
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(
            to_encode,
            settings.ACCESS_TOKEN_SECRET_KEY,
            algorithm=settings.ACCESS_TOKEN_ALGORITHM,
        )

    def crear_ticket_websocket(self, rut: str, sid: str) -> str:
        """Ticket de un solo propósito que autoriza abrir el WebSocket de avisos.

        Incluye ``sid`` para que el handshake pueda validar que la sesión sigue viva.
        """
        ahora = datetime.now(timezone.utc)
        payload = {
            'rut': rut,
            'sid': sid,
            'proposito': 'ws',
            'iat': ahora,
            'exp': ahora + timedelta(seconds=settings.CRM_WS_TICKET_TTL_SEGUNDOS),
        }
        return jwt.encode(
            payload,
            settings.ACCESS_TOKEN_SECRET_KEY,
            algorithm=settings.ACCESS_TOKEN_ALGORITHM,
        )

    def decodificar_token(self, token: str) -> dict[str, Any] | None:
        try:
            payload = jwt.decode(
                token,
                settings.ACCESS_TOKEN_SECRET_KEY,
                algorithms=[settings.ACCESS_TOKEN_ALGORITHM]
            )
            return payload
        except JWTError:
            return None

    # ── Sesiones y refresh tokens ───────────────────────────────

    def _requiere_sesiones(self) -> RepositorioSesiones:
        if self._sesiones is None:
            raise RuntimeError(
                "JwtAuthenticationService requiere un RepositorioSesiones "
                "para operaciones de sesión y refresh tokens."
            )
        return self._sesiones

    @staticmethod
    def _hash_token(token_plano: str) -> str:
        return hashlib.sha256(token_plano.encode()).hexdigest()

    def crear_sesion_y_tokens(
        self,
        usuario: Usuario,
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[str, str]:
        sesiones = self._requiere_sesiones()
        ahora = datetime.now(timezone.utc)
        sesion_expira = ahora + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DIAS)
        refresh_expira = ahora + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DIAS)

        sesion_id = sesiones.crear_sesion(
            rut_usuario=usuario.rut,
            ip=ip,
            user_agent=user_agent,
            expira_en=sesion_expira,
        )

        # Access token con sid y jti (claims completos desde el usuario)
        access_token = self.crear_access_token(usuario, sid=str(sesion_id))

        # Refresh token opaco
        refresh_token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(refresh_token)
        sesiones.guardar_refresh_token(
            sesion_id=sesion_id,
            token_hash=token_hash,
            expira_en=refresh_expira,
        )

        return access_token, refresh_token

    def rotar_refresh_token(self, refresh_token_plano: str) -> tuple[Sesion, str]:
        """Valida el refresh token y rota la familia.

        No emite el access token: el caso de uso lo arma con el usuario
        actualizado desde la base de datos (mismos claims que el login).
        """
        sesiones = self._requiere_sesiones()
        ahora = datetime.now(timezone.utc)
        token_hash = self._hash_token(refresh_token_plano)

        registro = sesiones.obtener_sesion_por_refresh_hash(token_hash)
        if registro is None:
            raise RefreshTokenInvalidoError()

        en_ventana_de_gracia = False

        # Token ya usado → posible robo o refresco concurrente
        if registro['token_usado_en'] is not None:
            grace = timedelta(seconds=settings.REFRESH_TOKEN_REUSE_GRACE_SEGUNDOS)
            if ahora > registro['token_usado_en'] + grace:
                # Fuera de ventana de gracia: revocar toda la familia
                sesiones.revocar_sesion(
                    registro['sesion_id'],
                    motivo='reuse_detectado',
                )
                raise RefreshTokenReusadoError()
            # Dentro de la gracia: refresco concurrente (dos pestañas).
            # Rotar de todos modos de forma idempotente.
            en_ventana_de_gracia = True

        if not en_ventana_de_gracia:
            # Token expirado
            if ahora > registro['token_expira_en']:
                raise RefreshTokenInvalidoError()

            # Sesión revocada o expirada
            if registro['sesion_revocado_en'] is not None:
                raise RefreshTokenInvalidoError()
            if ahora > registro['sesion_expira_en']:
                raise RefreshTokenInvalidoError()

        sesion_id = registro['sesion_id']
        sesion = sesiones.obtener_sesion_viva(sesion_id)
        if sesion is None:
            raise RefreshTokenInvalidoError()

        # Rotar: emitir nuevo refresh token y marcar el anterior
        nuevo_refresh = secrets.token_urlsafe(32)
        nuevo_hash = self._hash_token(nuevo_refresh)
        nuevo_token_id = sesiones.guardar_refresh_token(
            sesion_id=sesion_id,
            token_hash=nuevo_hash,
            expira_en=ahora + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DIAS),
        )
        sesiones.marcar_refresh_usado(registro['token_id'], nuevo_token_id)
        sesiones.actualizar_ultimo_acceso(sesion_id)

        return sesion, nuevo_refresh

    def revocar_sesion(self, sesion_id: UUID, motivo: str) -> None:
        self._requiere_sesiones().revocar_sesion(sesion_id, motivo)

    def revocar_todas_las_sesiones(self, rut: str, motivo: str) -> None:
        self._requiere_sesiones().revocar_sesiones_usuario(rut, motivo)

    def obtener_sesion_viva(self, sesion_id: UUID) -> Sesion | None:
        return self._requiere_sesiones().obtener_sesion_viva(sesion_id)
