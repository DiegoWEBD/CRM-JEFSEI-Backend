from abc import ABC, abstractmethod

from app.dominio.historial_estado.historial_estado import HistorialEstado


class RepositorioHistorialEstado(ABC):

    @abstractmethod
    def buscar_historial_proceso_comercial(self, id_proceso_comercial: int) -> list[HistorialEstado]:
        pass