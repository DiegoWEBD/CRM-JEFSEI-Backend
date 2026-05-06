from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.estados.estado_particular.estado_particular import EstadoParticular
from app.dominio.plan_pago.plan_pago import PlanPago
from app.dominio.poliza.poliza import Poliza
from app.dominio.usuario.usuario import Usuario

class EvaluacionRiesgo:
    def __init__(
        self, 
        id: int, 
        cotizaciones: list[Cotizacion], 
        ej_comercial: Usuario, 
        id_prospecto: int, 
        observaciones: str, 
        estado: EstadoParticular, 
        ej_evaluacion: Usuario | None = None, 
        poliza: Poliza | None = None, 
        plan_pago: PlanPago | None = None
    ):
        self.id = id
        self.cotizaciones = cotizaciones
        self.ej_evaluacion = ej_evaluacion
        self.ej_comercial = ej_comercial
        self.id_prospecto = id_prospecto
        self.observaciones = observaciones
        self.estado = estado
        self.poliza = poliza
        self.plan_pago = plan_pago