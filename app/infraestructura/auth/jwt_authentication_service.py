import os
import secrets
import hashlib
from typing import Any, Optional
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from app.aplicacion.auth.authentication_service import AuthenticationService
from jose import jwt, JWTError
from app.core.config import settings

# Bytes de entropía del refresh token. Va en claro al cliente y se almacena
# hasheado, así que necesita ser impredecible, no un JWT.
REFRESH_TOKEN_BYTES = 32


class JwtAuthenticationService(AuthenticationService):

    def __init__(self):
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto"
        )

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verificar_password(self, password_texto_plano: str, password_encriptada: str) -> bool:
        return self.pwd_context.verify(password_texto_plano, password_encriptada)

    def crear_access_token(self, data: dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})

        return jwt.encode(
            to_encode,
            settings.ACCESS_TOKEN_SECRET_KEY,
            algorithm=settings.ACCESS_TOKEN_ALGORITHM
        )

    def crear_access_token_de_sesion(
        self,
        data: dict[str, Any],
        id_sesion: str,
    ) -> str:
        """Access token con ``jti`` = id de sesión.

        El access token vive 15 minutos; la sesión en la base es la que manda
        sobre la vigencia real, así que un token no vigente no alcanza para
        abrir un endpoint.
        """
        to_encode = data.copy()
        ahora = datetime.now(timezone.utc)
        to_encode.update({
            'jti': id_sesion,
            'iat': ahora,
            'exp': ahora + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        })
        return jwt.encode(
            to_encode,
            settings.ACCESS_TOKEN_SECRET_KEY,
            algorithm=settings.ACCESS_TOKEN_ALGORITHM,
        )

    def crear_refresh_token(self, id_sesion: str) -> str:
        """Refresh token opaco, no un JWT.

        Se genera como ``<id_sesion>.<secreto>``: el id de sesión viaja para no
        obligar a un lookup adicional, y el secreto aleatorio es lo que se
        hashea y se valida.
        """
        secreto = secrets.token_urlsafe(REFRESH_TOKEN_BYTES)
        return f'{id_sesion}.{secreto}'

    def hashear_refresh_token(self, refresh_token: str) -> str:
        return hashlib.sha256(refresh_token.encode('utf-8')).hexdigest()

    def extraer_id_sesion_de_refresh(self, refresh_token: str) -> Optional[str]:
        return refresh_token.split('.', 1)[0] if '.' in refresh_token else None

    def crear_ticket_websocket(self, rut: str) -> str:
        """Ticket de un solo propósito que autoriza abrir el WebSocket de avisos.

        A diferencia del access token no sirve para llamar a la API: solo tiene
        el claim ``proposito='ws'`` y vive ``CRM_WS_TICKET_TTL_SEGUNDOS``.
        """
        ahora = datetime.now(timezone.utc)
        payload = {
            'rut': rut,
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