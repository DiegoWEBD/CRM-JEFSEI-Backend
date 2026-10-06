import hashlib
import secrets
from typing import Any
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from passlib.context import CryptContext
from jose import jwt, JWTError

from app.aplicacion.auth.authentication_service import AuthenticationService
from app.core.config import settings
from app.dominio.auth.exceptions import RefreshTokenInvalidoError, RefreshTokenReusadoError
from app.dominio.auth.repositorio_sesiones import RepositorioSesiones
from app.dominio.auth.sesion import Sesion


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

    def crear_access_token(self, data: dict[str, Any]) -> str:
        to_encode = data.copy()
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
        claims: dict[str, Any],
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[str, str]:
        sesiones = self._requiere_sesiones()
        ahora = datetime.now(timezone.utc)
        sesion_expira = ahora + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DIAS)
        refresh_expira = ahora + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DIAS)

        sesion_id = sesiones.crear_sesion(
            rut_usuario=claims["rut"],
            ip=ip,
            user_agent=user_agent,
            expira_en=sesion_expira,
        )

        # Access token con sid y jti
        claims_con_sesion = {**claims, "sid": str(sesion_id), "jti": str(uuid4())}
        access_token = self.crear_access_token(claims_con_sesion)

        # Refresh token opaco
        refresh_token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(refresh_token)
        sesiones.guardar_refresh_token(
            sesion_id=sesion_id,
            token_hash=token_hash,
            expira_en=refresh_expira,
        )

        return access_token, refresh_token

    def rotar_tokens(self, refresh_token_plano: str) -> tuple[str, str]:
        print('Rotando tokens con refresh token:', refresh_token_plano)
        sesiones = self._requiere_sesiones()
        ahora = datetime.now(timezone.utc)
        token_hash = self._hash_token(refresh_token_plano)

        registro = sesiones.obtener_sesion_por_refresh_hash(token_hash)
        if registro is None:
            raise RefreshTokenInvalidoError()

        # Token ya usado → posible robo
        if registro['token_usado_en'] is not None:
            grace = timedelta(seconds=settings.REFRESH_TOKEN_REUSE_GRACE_SEGUNDOS)
            if ahora > registro['token_usado_en'] + grace:
                # Fuera de ventana de gracia: revocar toda la familia
                sesiones.revocar_sesion(
                    registro['sesion_id'],
                    motivo='reuse_detectado',
                )
                raise RefreshTokenReusadoError()
            # Dentro de la gracia: respuesta idempotente (concurrente)
            # Buscamos el token de reemplazo y devolvemos los mismos datos
            raise RefreshTokenInvalidoError()  # el cliente debe reintentar

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

        # Nuevo access token con los mismos claims de identidad
        nuevo_access = self.crear_access_token({
            "rut": sesion.rut_usuario,
            "sid": str(sesion_id),
            "jti": str(uuid4()),
            # Los roles/permisos se revalidan en get_current_user,
            # no se cachean en el token de refresh.
        })

        print('Tokens rotados. Nuevo access token:', nuevo_access)
        print('Nuevo refresh token:', nuevo_refresh)
        return nuevo_access, nuevo_refresh

    def revocar_sesion(self, sesion_id: UUID, motivo: str) -> None:
        self._requiere_sesiones().revocar_sesion(sesion_id, motivo)

    def revocar_todas_las_sesiones(self, rut: str, motivo: str) -> None:
        self._requiere_sesiones().revocar_sesiones_usuario(rut, motivo)

    def obtener_sesion_viva(self, sesion_id: UUID) -> Sesion | None:
        return self._requiere_sesiones().obtener_sesion_viva(sesion_id)
