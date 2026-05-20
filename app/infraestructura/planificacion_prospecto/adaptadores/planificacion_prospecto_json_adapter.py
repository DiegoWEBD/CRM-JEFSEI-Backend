from app.dominio.planificacion_prospecto.planificacion_prospecto import PlanificacionProspecto
from app.presentacion.api.planificacion_prospecto.dto.planificacion_prospecto_json import PlanificacionProspectoJson


class PlanificacionProspectoJsonAdapter:

    def __init__(self, planificacion: PlanificacionProspecto):
        self.planificacion = planificacion

    def to_planificacion_prospecto_json(self) -> PlanificacionProspectoJson:
        return PlanificacionProspectoJson(
            prima_vigente=self.planificacion.prima_vigente,
            company_poliza=self.planificacion.company_poliza.nombre,
            termino_vigencia=self.planificacion.termino_vigencia.isoformat(),
            monto_asegurado_vigente=self.planificacion.monto_asegurado_vigente,
            fecha_envio_cotizacion=self.planificacion.fecha_envio_cotizacion.isoformat()
        )