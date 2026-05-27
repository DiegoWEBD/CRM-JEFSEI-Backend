from app.dominio.evaluacion_riesgo.repositorio_evaluaciones_riesgo import RepositorioEvaluacionesRiesgo


class SolicitarEstudioCondominioUseCase:

    def __init__(
        self,
        repositorio_evaluaciones_riesgo: RepositorioEvaluacionesRiesgo
    ) -> None:
        self.repositorio_evaluaciones_riesgo = repositorio_evaluaciones_riesgo

    def ejecutar(self, id_prospecto: int):
        pass