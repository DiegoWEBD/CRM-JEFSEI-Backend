from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.estados.estado_particular.estado_particular import EstadoParticular
from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo
from app.dominio.plan_pago.plan_pago import PlanPago
from app.dominio.poliza.poliza import Poliza
from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.usuario.usuario import Usuario

class EvaluacionRiesgoCondominio(EvaluacionRiesgo):
    def __init__(
        self, 
        id: int, 
        cotizaciones: list[Cotizacion], 
        ej_comercial: Usuario, 
        prospecto: Prospecto, 
        observaciones: str, 
        estado: EstadoParticular,
        tiene_locales_comerciales: bool | None = None,
        uso_del_condominio: str | None = None,
        numero_pisos: int | None = None,
        numero_torres: int | None = None,
        cantidad_departamentos: int | None = None,
        cantidad_subterraneos: int | None = None,
        tiene_piscina: bool | None = None,
        year_construccion: int | None = None,
        metros_cuadrados: int | None = None,
        monto_asegurado: float | None = None,
        ej_evaluacion: Usuario | None = None, 
        poliza: Poliza | None = None, 
        plan_pago: PlanPago | None = None
    ):
        super().__init__(id, cotizaciones, ej_comercial, prospecto, observaciones, estado, ej_evaluacion, poliza, plan_pago)
        self.tiene_locales_comerciales = tiene_locales_comerciales
        self.uso_del_condominio = uso_del_condominio
        self.numero_pisos = numero_pisos
        self.numero_torres = numero_torres
        self.cantidad_departamentos = cantidad_departamentos
        self.cantidad_subterraneos = cantidad_subterraneos
        self.tiene_piscina = tiene_piscina
        self.year_construccion = year_construccion
        self.metros_cuadrados = metros_cuadrados
        self.monto_asegurado = monto_asegurado