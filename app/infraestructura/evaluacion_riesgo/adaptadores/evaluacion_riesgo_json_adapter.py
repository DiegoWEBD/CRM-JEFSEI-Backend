
from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo
from app.infraestructura.cotizacion.adaptadores.cotizacion_json_adapter import CotizacionJsonAdapter
from app.infraestructura.estudio_comercial_condominio.adaptadores.estudio_comercial_condominio_json_adapter import EstudioComercialCondominioJsonAdapter
from app.presentacion.api.evaluacion_riesgo.dto.evaluacion_riesgo_json import EvaluacionRiesgoJson


class EvaluacionRiesgoJsonAdapter:

    def __init__(self, evaluacion_riesgo: EvaluacionRiesgo):
        self.evaluacion_riesgo = evaluacion_riesgo

    def to_evaluacion_riesgo_json(self) -> EvaluacionRiesgoJson:
        return EvaluacionRiesgoJson(
            uf_por_metro_cuadrado=self.evaluacion_riesgo.uf_por_metro_cuadrado,
            porcentaje_depreciacion=self.evaluacion_riesgo.porcentaje_depreciacion,
            porcentaje_espacios_comunes=self.evaluacion_riesgo.porcentaje_espacios_comunes,
            observaciones=self.evaluacion_riesgo.observaciones,
            cotizaciones=[CotizacionJsonAdapter(cotizacion).to_cotizacion_json() for cotizacion in self.evaluacion_riesgo.cotizaciones],
            estudio=EstudioComercialCondominioJsonAdapter(self.evaluacion_riesgo.estudio).to_json() if self.evaluacion_riesgo.estudio else None
        )