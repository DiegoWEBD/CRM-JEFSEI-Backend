from abc import ABC, abstractmethod

from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.celda_excel import CeldaExcel
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.hoja_excel import HojaExcel


class LectorAlicuotasExcel(ABC):
    """Lectura de libros .xlsx independiente de la biblioteca usada."""

    @abstractmethod
    def obtener_hojas(self, contenido: bytes) -> list[HojaExcel]:
        pass

    @abstractmethod
    def leer_bloque(
        self,
        contenido: bytes,
        hoja: str,
        fila_desde: int,
        fila_hasta: int,
        columnas: list[int],
    ) -> list[list[CeldaExcel]]:
        """Devuelve las filas del bloque; cada fila lista las celdas en el orden de `columnas`."""
        pass
