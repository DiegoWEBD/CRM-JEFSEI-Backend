from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.cotizacion.cotizacion import Cotizacion


class DetalleEstudioComercial:

    def __init__(
        self,
        cotizacion: Cotizacion,
        porcentaje_infraseguro: float,
        iva_prima_afecta: float,
        prima_neta: float,
        prima_bruta: float
    ):
        self.iva_prima_afecta = iva_prima_afecta
        self.prima_neta = prima_neta
        self.prima_bruta = prima_bruta
        self.cotizacion = cotizacion
        self.porcentaje_infraseguro = porcentaje_infraseguro