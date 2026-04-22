import os
from typing import Any
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from app.aplicacion.auth.authentication_service import AuthenticationService
from jose import jwt, JWTError
from app.core.config import settings

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