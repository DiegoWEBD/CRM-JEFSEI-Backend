from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.plan_pago.plan_pago import PlanPago
from app.dominio.poliza.poliza import Poliza
from app.dominio.usuario.usuario import Usuario

class EvaluacionRiesgo:
    def __init__(
        self, 
        cotizaciones: list[Cotizacion], 
        ej_comercial: Usuario, 
        observaciones: str | None = None, 
        id: int | None = None, 
        ej_evaluacion: Usuario | None = None, 
        poliza: Poliza | None = None, 
        plan_pago: PlanPago | None = None
    ):
        self.id = id
        self.cotizaciones = cotizaciones
        self.ej_evaluacion = ej_evaluacion
        self.ej_comercial = ej_comercial
        self.observaciones = observaciones
        self.poliza = poliza
        self.plan_pago = plan_pago