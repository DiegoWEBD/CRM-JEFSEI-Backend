import os
from typing import Any
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from app.aplicacion.auth.authentication_service import AuthenticationService
from jose import jwt, JWTError

class JwtAuthenticationService(AuthenticationService):

    def __init__(self):
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto"
        )
        self.SECRET_KEY = os.getenv("ACCESS_TOKEN_SECRET_KEY")
        self.ALGORITHM = os.getenv("ACCESS_TOKEN_ALGORITHM")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

    def encriptar_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verificar_password(self, password_texto_plano: str, password_encriptada: str) -> bool:
        return self.pwd_context.verify(password_texto_plano, password_encriptada)

    def crear_access_token(self, data: dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})

        return jwt.encode(
            to_encode,
            self.SECRET_KEY,
            algorithm=self.ALGORITHM
        )

    def decodificar_token(self, token: str) -> dict[str, Any] | None:
        try:
            payload = jwt.decode(
                token,
                self.SECRET_KEY,
                algorithms=[self.ALGORITHM]
            )
            return payload

        except JWTError:
            return None