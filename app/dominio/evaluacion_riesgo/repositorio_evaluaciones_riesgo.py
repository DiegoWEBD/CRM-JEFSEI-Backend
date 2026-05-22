from abc import ABC, abstractmethod
from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo


class RepositorioEvaluacionesRiesgo(ABC):
    
    @abstractmethod
    def registrar(self, evaluacion: EvaluacionRiesgo) -> None:
        pass

    @abstractmethod
    def buscar(self, rut: str) -> EvaluacionRiesgo | None:
        pass