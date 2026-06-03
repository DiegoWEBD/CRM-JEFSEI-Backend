from app.dominio.cotizacion.cotizacion import Cotizacion
from app.presentacion.api.cotizacion.dto.cotizacion_json import CotizacionJson


class CotizacionJsonAdapter:

    def __init__(self, cotizacion: Cotizacion) -> None:
        self.cotizacion = cotizacion

    def to_cotizacion_json(self) -> CotizacionJson:
        return CotizacionJson(
            id=self.cotizacion.id,
            monto_total_asegurado=self.cotizacion.monto_total_asegurado,
            tasa_afecta=self.cotizacion.tasa_afecta,
            tasa_excenta=self.cotizacion.tasa_excenta,
            tasa_politica=self.cotizacion.tasa_politica,
            prima_adicional_asistencia=self.cotizacion.prima_adicional_asistencia,
            company=self.cotizacion.company.nombre,
            fecha_emision=self.cotizacion.fecha_emision.isoformat(),
            fecha_vencimiento=self.cotizacion.fecha_vencimiento.isoformat()
        )