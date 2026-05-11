from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo
from app.infraestructura.usuario.adaptadores.usuario_json_resumen_adapter import UsuarioJsonResumenAdapter
from app.presentacion.api.evaluacion_riesgo.dto.evaluacion_riesgo_json import EvaluacionRiesgoJson


class EvaluacionRiesgoJsonAdapter:

    def __init__(self, evaluacion_riesgo: EvaluacionRiesgo):
        self.evaluacion_riesgo = evaluacion_riesgo

    def to_evaluacion_riesgo_json(self) -> EvaluacionRiesgoJson:
        return EvaluacionRiesgoJson(
            id=self.evaluacion_riesgo.id,
            ej_comercial=UsuarioJsonResumenAdapter(self.evaluacion_riesgo.ej_comercial).to_usuario_json_resumen(),
            observaciones=self.evaluacion_riesgo.observaciones,
            ej_evaluacion=UsuarioJsonResumenAdapter(self.evaluacion_riesgo.ej_evaluacion).to_usuario_json_resumen() if self.evaluacion_riesgo.ej_evaluacion else None,
        )