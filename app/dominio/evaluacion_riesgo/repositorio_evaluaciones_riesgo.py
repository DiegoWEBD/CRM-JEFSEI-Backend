from abc import ABC, abstractmethod
from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo


class RepositorioEvaluacionesRiesgo(ABC):

    @abstractmethod
    def buscar_evaluacion(self, id_prospecto: int) -> EvaluacionRiesgo | None:
        pass