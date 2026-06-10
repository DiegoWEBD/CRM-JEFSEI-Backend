from abc import ABC, abstractmethod


class ConteoEstadosProcesosComercialesService(ABC):
    
    @abstractmethod
    def contar_procesos_comerciales_por_estado(self):
        pass