from app.dominio.company_seguros.company_seguros import CompanySeguros


class DetalleEstudioComercial:

    def __init__(
        self,
        monto_total_asegurado: float,
        porcentaje_infraseguro: float,
        iva_prima_afecta: float,
        prima_neta: float,
        prima_bruta: float, 
        tasa_afecta: float, 
        tasa_excenta: float,
        company: CompanySeguros
    ):
        self.iva_prima_afecta = iva_prima_afecta
        self.prima_neta = prima_neta
        self.prima_bruta = prima_bruta
        self.tasa_afecta = tasa_afecta
        self.tasa_excenta = tasa_excenta
        self.company = company
        self.monto_total_asegurado = monto_total_asegurado
        self.porcentaje_infraseguro = porcentaje_infraseguro