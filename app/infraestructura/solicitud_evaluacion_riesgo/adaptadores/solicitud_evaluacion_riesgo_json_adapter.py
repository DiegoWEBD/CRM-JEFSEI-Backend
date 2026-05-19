from app.dominio.solicitud_evaluacion_riesgo.solicitud_evaluacion_riesgo import SolicitudEvaluacionRiesgo
from app.presentacion.api.solicitud_evaluacion_riesgo.dto.solicitud_evaluacion_riesgo_json import SolicitudEvaluacionRiesgoJson


class SolicitudEvaluacionRiesgoJsonAdapter:

    def __init__(self, solicitud: SolicitudEvaluacionRiesgo):     
        self.solicitud = solicitud

    def to_solicitud_evaluacion_riesgo_json(self) -> SolicitudEvaluacionRiesgoJson:
        return SolicitudEvaluacionRiesgoJson(
            fecha_solicitud=self.solicitud.fecha_solicitud.isoformat(),
            prioridad=self.solicitud.prioridad
        )