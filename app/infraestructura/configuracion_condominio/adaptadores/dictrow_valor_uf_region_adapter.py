from psycopg.rows import DictRow

from app.dominio.configuracion_condominio.valor_uf_region import ValorUfRegion


class DictRowValorUfRegionAdapter:

    def __init__(self, row: DictRow):
        if row is None:
            raise ValueError("Valor UF region inválido")

        self.row = row

    def to_valor_uf_region(self) -> ValorUfRegion:
        return ValorUfRegion(
            id=self.row["id"],
            region=self.row["region"],
            valor_uf_m2=self.row["valor_uf_m2"],
        )
