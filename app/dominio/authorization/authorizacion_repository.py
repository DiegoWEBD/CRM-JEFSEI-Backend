from abc import ABC, abstractmethod


class AuthorizationRepository(ABC):
    
    @abstractmethod
    def usuario_puede_ver_solicitud_cotizacion(self, rut_usuario: str, id_solicitud: int) -> bool:
        pass