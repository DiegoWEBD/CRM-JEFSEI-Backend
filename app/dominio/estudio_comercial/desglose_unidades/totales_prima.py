class TotalesPrima:
    """Resultado del primer cálculo de una cotización a partir de sus tasas."""

    def __init__(
        self,
        monto_asegurado: float,
        prima_afecta: float,
        prima_excenta: float,
        prima_iva: float,
        prima_neta: float,
        prima_bruta: float,
    ) -> None:
        self.monto_asegurado = monto_asegurado
        self.prima_afecta = prima_afecta
        self.prima_excenta = prima_excenta
        self.prima_iva = prima_iva
        self.prima_neta = prima_neta
        self.prima_bruta = prima_bruta
