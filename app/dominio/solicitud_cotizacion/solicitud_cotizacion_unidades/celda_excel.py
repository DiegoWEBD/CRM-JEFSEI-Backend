class CeldaExcel:
    """Valor mínimo de una celda, independiente de la biblioteca de lectura."""

    def __init__(
        self,
        valor=None,
        formato_numerico: str | None = None,
        formula_sin_resultado: bool = False,
    ) -> None:
        self.valor = valor
        self.formato_numerico = formato_numerico
        self.formula_sin_resultado = formula_sin_resultado
