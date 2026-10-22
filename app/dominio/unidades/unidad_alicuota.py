class UnidadAlicuota:

    def __init__(
        self,
        identificador_unidad: str,
        prorrateo: float,
        fila_origen: int,
    ) -> None:
        self.identificador_unidad = identificador_unidad
        self.prorrateo = prorrateo
        self.fila_origen = fila_origen
