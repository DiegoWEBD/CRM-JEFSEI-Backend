from abc import ABC, abstractmethod

from app.dominio.historial_estado.historial_estado_proceso_comercial import HistorialEstadoProcesoComercial


class RepositorioHistorialEstadoProcesosComerciales(ABC):

    @abstractmethod
    def registrar(self, historial: HistorialEstadoProcesoComercial) -> None:
        """Inserta el registro en el historial y actualiza
        ProcesoComercial.codigo_estado_actual al mismo estado."""
        pass