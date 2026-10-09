from psycopg.rows import DictRow

from app.dominio.estado_informativo_proceso_comercial.transicion_estado_proceso_comercial import TransicionEstadoProcesoComercial


class DictRowTransicionEstadoAdapter:

    def __init__(self, row: DictRow) -> None:
        self.row = row

    def to_transicion_estado_proceso_comercial(self) -> TransicionEstadoProcesoComercial:
        return TransicionEstadoProcesoComercial(
            codigo_estado_origen=self.row['codigo_estado_origen'],
            codigo_estado_destino=self.row['codigo_estado_destino'],
            nombre_estado_destino=self.row['nombre_estado_destino'],
            es_manual=self.row['es_manual'],
            es_principal=self.row['es_principal'],
            accion_requerida=self.row['accion_requerida'],
        )