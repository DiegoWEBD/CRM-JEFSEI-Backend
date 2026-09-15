from app.dominio.cotizacion.cotizacion import Cotizacion


class DetalleEstudioComercial:

    def __init__(
        self,
        cotizacion: Cotizacion,
        monto_asegurado: float,
        porcentaje_infraseguro: float,
        prima_neta: float,
        prima_bruta: float,
        valor_cuota: float
    ):
        self.prima_neta = prima_neta
        self.prima_bruta = prima_bruta
        self.cotizacion = cotizacion
        self.monto_asegurado = monto_asegurado
        self.porcentaje_infraseguro = porcentaje_infraseguro
        self.valor_cuota = valor_cuota