class EvaluacionRiesgo:
    def __init__(
        self, 
        uf_por_metro_cuadrado: float | None,
        porcentaje_depreciacion: float | None,
        porcentaje_espacios_comunes: float | None,
        observaciones: str | None = None, 
        id: int | None = None
    ):
        self.id = id
        self.observaciones = observaciones
        self.uf_por_metro_cuadrado = uf_por_metro_cuadrado
        self.porcentaje_depreciacion = porcentaje_depreciacion
        self.porcentaje_espacios_comunes = porcentaje_espacios_comunes