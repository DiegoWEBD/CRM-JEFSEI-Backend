from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.estudio_comercial.estudio_comercial_condominio.estudio_comercial_condominio import EstudioComercialCondominio
from app.dominio.plan_pago.plan_pago import PlanPago
from app.dominio.poliza.poliza import Poliza

class EvaluacionRiesgo:
    def __init__(
        self, 
        uf_por_metro_cuadrado: float | None,
        monto_asegurado_actual: float | None,
        porcentaje_depreciacion: float | None,
        porcentaje_espacios_comunes: float | None,
        observaciones: str | None = None, 
        id: int | None = None, 
        cotizaciones: list[Cotizacion] = [],
        poliza: Poliza | None = None, 
        plan_pago: PlanPago | None = None,
        estudios: list[EstudioComercialCondominio] | None = None
    ):
        self.id = id
        self.cotizaciones = cotizaciones
        self.observaciones = observaciones
        self.poliza = poliza
        self.plan_pago = plan_pago
        self.monto_asegurado_actual = monto_asegurado_actual
        self.uf_por_metro_cuadrado = uf_por_metro_cuadrado
        self.porcentaje_depreciacion = porcentaje_depreciacion
        self.porcentaje_espacios_comunes = porcentaje_espacios_comunes
        self.estudios = estudios