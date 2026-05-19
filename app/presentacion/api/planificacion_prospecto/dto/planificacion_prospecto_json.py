from pydantic import BaseModel


class PlanificacionProspectoJson(BaseModel):
    prima_vigente: float
    company_poliza: str
    termino_vigencia: str
    monto_asegurado_vigente: float
    fecha_envio_cotizacion: str | None