from psycopg.rows import DictRow

from app.dominio.configuracion_condominio.parametros_depreciacion import ParametrosDepreciacion


class DictRowParametrosDepreciacionAdapter:

    def __init__(self, row: DictRow):
        if row is None:
            raise ValueError("Parámetros de depreciación inválidos")

        self.row = row

    def to_parametros_depreciacion(self) -> ParametrosDepreciacion:
        return ParametrosDepreciacion(
            id=self.row["id"],
            antiguedad_sin_depreciacion=self.row["antiguedad_sin_depreciacion"],
            porcentaje_por_anio=self.row["porcentaje_por_anio"],
            antiguedad_maxima=self.row["antiguedad_maxima"],
            porcentaje_maximo=self.row["porcentaje_maximo"],
        )
