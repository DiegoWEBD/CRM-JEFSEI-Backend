from psycopg.rows import DictRow

from app.dominio.unidades.unidad_alicuota import UnidadAlicuota


class DictRowUnidadAlicuotaAdapter:

    def __init__(self, row: DictRow) -> None:
        self.row = row

    def to_unidad_alicuota(self) -> UnidadAlicuota:
        return UnidadAlicuota(
            identificador_unidad=self.row['identificador_unidad'],
            prorrateo=self.row['prorrateo'],
            fila_origen=self.row['fila_origen'],
        )
    