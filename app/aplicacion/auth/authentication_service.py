from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any

class AuthenticationService(ABC):

    @abstractmethod
    def encriptar_password(password: str) -> str:
        pass

    @abstractmethod
    def verificar_password(password_texto_plano: str, password_encriptada: str) -> bool:
        pass

    @abstractmethod
    def crear_access_token(data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    def decodificar_token(token: str) -> dict[str, Any] | None:
        pass