from abc import ABC, abstractmethod

from app.dominio.cotizacion.cotizacion import Cotizacion


class RepositorioCotizaciones(ABC):

    @abstractmethod
    def obtener_por_solicitud(self, id_solicitud: int) -> list[Cotizacion]:
        pass

    @abstractmethod
    def obtener_por_id(self, id_cotizacion: int) -> Cotizacion:
        pass

    @abstractmethod
    def registrar_cotizacion_a_solicitud(self, id_solicitud: int, cotizacion: Cotizacion, rut_usuario: str) -> int | None:
        """Inserta la cotización y actualiza el estado del proceso comercial.

        Devuelve el id_proceso_comercial resuelto (None si la solicitud no
        existe) para que el caso de uso marque las alertas del proceso.
        """
        pass

    @abstractmethod
    def registrar_renovacion_cotizada(self, numero_poliza_renovacion: str):
        pass