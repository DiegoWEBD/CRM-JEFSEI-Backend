from abc import ABC, abstractmethod

from app.dominio.historial_estado.historial_estado import HistorialEstado


class RepositorioHistorialEstado(ABC):

    @abstractmethod
    def buscar_historial_prospecto(self, id_prospecto: int) -> list[HistorialEstado]:
        pass