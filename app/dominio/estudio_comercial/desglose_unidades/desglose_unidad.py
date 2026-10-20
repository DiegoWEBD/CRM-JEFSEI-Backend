class DesgloseUnidad:
    """Valores prorrateados de una cotización sobre una unidad de la alícuota."""

    def __init__(
        self,
        identificador_unidad: str,
        prorrateo: float,
        monto_asegurado: float,
        prima_afecta: float,
        prima_excenta: float,
        prima_neta: float,
        prima_iva: float,
        prima_bruta: float,
    ) -> None:
        self.identificador_unidad = identificador_unidad
        self.prorrateo = prorrateo
        self.monto_asegurado = monto_asegurado
        self.prima_afecta = prima_afecta
        self.prima_excenta = prima_excenta
        self.prima_neta = prima_neta
        self.prima_iva = prima_iva
        self.prima_bruta = prima_bruta
