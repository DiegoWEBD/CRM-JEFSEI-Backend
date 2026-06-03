from datetime import datetime

from app.dominio.company_seguros.company_seguros import CompanySeguros


class PlanificacionProspecto:

    def __init__(
        self,
        prima_vigente: float,
        company_poliza: CompanySeguros,
        termino_vigencia: datetime,
        monto_asegurado_vigente: float,
        fecha_envio_cotizacion: datetime | None
    ):
        self.prima_vigente = prima_vigente
        self.termino_vigencia = termino_vigencia
        self.monto_asegurado_vigente = monto_asegurado_vigente
        self.fecha_envio_cotizacion = fecha_envio_cotizacion
        self.company_poliza = company_poliza