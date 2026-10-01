from abc import ABC, abstractmethod
from typing import Any, Optional

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

    @abstractmethod
    def crear_access_token_de_sesion(
        self,
        data: dict[str, Any],
        id_sesion: str,
    ) -> str:
        """Access token ligado a una sesión persistida.

        El claim ``jti`` es el id de la sesión: es lo que permite que la
        auditoría atribuya la acción a una sesión concreta y que una revocación
        de esa sesión invalide el token.
        """
        pass

    @abstractmethod
    def crear_refresh_token(self, id_sesion: str) -> str:
        """Refresh token opaco. Viaja al cliente en claro, se guarda hasheado."""
        pass

    @abstractmethod
    def hashear_refresh_token(self, refresh_token: str) -> str:
        """Huella irreversible con la que se busca el token en la base."""
        pass