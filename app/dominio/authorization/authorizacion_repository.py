from abc import ABC, abstractmethod


class AuthorizationRepository(ABC):
    
    @abstractmethod
    def usuario_puede_ver_solicitud_cotizacion(self, rut_usuario: str, id_solicitud: int) -> bool:
        pass

    @abstractmethod
    def usuario_puede_gestionar_renovacion(self, rut_usuario: str, numero_poliza: str) -> bool:
        pass