from abc import ABC, abstractmethod

from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial


class RepositorioProcesosComerciales(ABC):
    
    @abstractmethod
    def obtener_procesos_comerciales(self, id_prospecto: int) -> list[ProcesoComercial]:
        pass