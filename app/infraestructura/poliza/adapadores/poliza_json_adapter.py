from app.dominio.poliza.poliza import Poliza
from app.infraestructura.company_seguros.adaptadores.company_seguros_json_adapter import CompanySegurosJsonAdapter
from app.presentacion.api.poliza.dto.poliza_json import PolizaJson


class PolizaJsonAdapter:

    def __init__(self, poliza: Poliza) -> None:
        self.poliza = poliza

    def to_json(self) -> PolizaJson:
        return PolizaJson(
            numero_poliza=self.poliza.numero_poliza,
            id_proceso_comercial=self.poliza.id_proceso_comercial,
            tipo=self.poliza.tipo,
            nombre_producto=self.poliza.nombre_producto,
            company=CompanySegurosJsonAdapter(self.poliza.company).to_json() if self.poliza.company else None,
            prima_neta=self.poliza.prima_neta,
            comision_corredora_pct=self.poliza.comision_corredora_pct,
            fecha_emision=self.poliza.fecha_emision.isoformat() if self.poliza.fecha_emision else None,
            inicio_vigencia=self.poliza.inicio_vigencia.isoformat() if self.poliza.inicio_vigencia else None,
            fin_vigencia=self.poliza.fin_vigencia.isoformat() if self.poliza.fin_vigencia else None,
            estado=self.poliza.estado,
            renovacion_cotizada=self.poliza.renovacion_cotizada
        )