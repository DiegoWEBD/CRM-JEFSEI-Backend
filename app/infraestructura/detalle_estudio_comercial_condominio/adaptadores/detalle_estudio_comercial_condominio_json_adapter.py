from app.dominio.estudio_comercial.detalle_estudio_comercial.detalle_estudio_comercial import DetalleEstudioComercial
from app.infraestructura.cotizacion.adaptadores.cotizacion_json_adapter import CotizacionJsonAdapter
from app.presentacion.api.detalle_estudio_comercial_condominio.dto.detalle_estudio_comercial_condominio_json import DetalleEstudioComercialCondominioJson


class DetalleEstudioComercialCondominioJsonAdapter:

    def __init__(self, detalle: DetalleEstudioComercial) -> None:
        self.detalle = detalle

    def to_json(self) -> DetalleEstudioComercialCondominioJson:
        return DetalleEstudioComercialCondominioJson(
            cotizacion=CotizacionJsonAdapter(self.detalle.cotizacion).to_cotizacion_json(),
            porcentaje_infraseguro=self.detalle.porcentaje_infraseguro,
            iva_prima_afecta=self.detalle.iva_prima_afecta,
            prima_neta=self.detalle.prima_neta,
            prima_bruta=self.detalle.prima_bruta
        )