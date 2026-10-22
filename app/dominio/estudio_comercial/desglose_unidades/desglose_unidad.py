class DesgloseUnidad:
    """Porción de una cotización que corresponde a una unidad de la alícuota."""

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
        prorrateo_pago: float | None = None,
        monto_reconstruccion: float | None = None,
        monto_asegurado_sugerido: float | None = None,
        valor_cuota_uf: float | None = None,
        valor_cuota_pesos: float | None = None,
    ) -> None:
        self.identificador_unidad = identificador_unidad
        self.prorrateo = prorrateo
        self.monto_asegurado = monto_asegurado
        self.prima_afecta = prima_afecta
        self.prima_excenta = prima_excenta
        self.prima_neta = prima_neta
        self.prima_iva = prima_iva
        self.prima_bruta = prima_bruta
        self.prorrateo_pago = prorrateo_pago
        self.monto_reconstruccion = monto_reconstruccion
        self.monto_asegurado_sugerido = monto_asegurado_sugerido
        self.valor_cuota_uf = valor_cuota_uf
        self.valor_cuota_pesos = valor_cuota_pesos
