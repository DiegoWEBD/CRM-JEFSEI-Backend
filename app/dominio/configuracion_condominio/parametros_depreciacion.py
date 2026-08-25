class ParametrosDepreciacion:

    def __init__(
        self,
        id: int | None,
        antiguedad_sin_depreciacion: int,
        porcentaje_por_anio: float,
        antiguedad_maxima: int,
        porcentaje_maximo: float
    ):
        self.id = id
        self.antiguedad_sin_depreciacion = antiguedad_sin_depreciacion
        self.porcentaje_por_anio = porcentaje_por_anio
        self.antiguedad_maxima = antiguedad_maxima
        self.porcentaje_maximo = porcentaje_maximo
