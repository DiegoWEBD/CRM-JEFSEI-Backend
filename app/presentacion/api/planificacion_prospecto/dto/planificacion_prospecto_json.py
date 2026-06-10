from pydantic import BaseModel


class PlanificacionProspectoJson(BaseModel):
    prima_vigente: float
    company_poliza: str | None
    termino_vigencia: str | None
    monto_asegurado_vigente: float | None
    fecha_envio_cotizacion: str | None