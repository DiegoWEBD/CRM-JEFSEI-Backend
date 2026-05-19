
from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo
from app.presentacion.api.evaluacion_riesgo.dto.evaluacion_riesgo_json import EvaluacionRiesgoJson


class EvaluacionRiesgoJsonAdapter:

    def __init__(self, evaluacion_riesgo: EvaluacionRiesgo):
        self.evaluacion_riesgo = evaluacion_riesgo

    def to_evaluacion_riesgo_json(self) -> EvaluacionRiesgoJson:
        return EvaluacionRiesgoJson(
            uf_por_metro_cuadrado=self.evaluacion_riesgo.uf_por_metro_cuadrado,
            monto_asegurado_actual=self.evaluacion_riesgo.monto_asegurado_actual,
            porcentaje_depreciacion=self.evaluacion_riesgo.porcentaje_depreciacion,
            porcentaje_espacios_comunes=self.evaluacion_riesgo.porcentaje_espacios_comunes,
            observaciones=self.evaluacion_riesgo.observaciones
        )