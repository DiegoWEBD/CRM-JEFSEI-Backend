from abc import ABC, abstractmethod

from app.dominio.cotizacion.cotizacion import Cotizacion


class RepositorioCotizaciones(ABC):

    @abstractmethod
    def obtener_por_solicitud(self, id_solicitud: int) -> list[Cotizacion]:
        pass

    @abstractmethod
    def obtener_por_id(self, id_cotizacion: int) -> Cotizacion | None:
        pass

    @abstractmethod
    def registrar_cotizacion_a_solicitud(self, id_solicitud: int, cotizacion: Cotizacion, rut_usuario: str) -> None:
        """Inserta la cotización y actualiza el estado del proceso comercial."""
        pass

    @abstractmethod
    def registrar_renovacion_cotizada(self, numero_poliza_renovacion: str):
        pass

    @abstractmethod
    def eliminar(self, cotizacion: Cotizacion) -> None:
        """Elimina la cotización. Solo persistencia."""
        pass

    @abstractmethod
    def actualizar(self, id_cotizacion: int, cotizacion: Cotizacion) -> None:
        """Actualiza los datos de la cotización. Solo persistencia."""
        pass

    @abstractmethod
    def cotizacion_pertenece_a_solicitud(self, cotizacion: Cotizacion, id_solicitud: int) -> bool:
        pass