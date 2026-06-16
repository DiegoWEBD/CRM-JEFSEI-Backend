from abc import ABC, abstractmethod

from app.dominio.cotizacion.cotizacion import Cotizacion


class RepositorioCotizaciones(ABC):

    @abstractmethod
    def obtener_por_solicitud(self, id_solicitud: int) -> list[Cotizacion]:
        pass

    @abstractmethod
    def registrar_cotizacion_a_solicitud(self, id_solicitud: int, cotizacion: Cotizacion, rut_usuario: str):
        pass

    @abstractmethod
    def registrar_cotizacion_sin_solicitud(self, cotizacion: Cotizacion):
        pass