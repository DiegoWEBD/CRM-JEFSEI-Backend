from abc import ABC, abstractmethod
from typing import Any

class AuthenticationService(ABC):

    @abstractmethod
    def hash_password(self, password: str) -> str:
        pass

    @abstractmethod
    def verificar_password(self, password_texto_plano: str, password_encriptada: str) -> bool:
        pass

    @abstractmethod
    def crear_access_token(self, data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    def decodificar_token(self, token: str) -> dict[str, Any] | None:
        pass