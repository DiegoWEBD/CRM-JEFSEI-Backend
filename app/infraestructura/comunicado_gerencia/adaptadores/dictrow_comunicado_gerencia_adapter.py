from psycopg.rows import DictRow

from app.dominio.comunicado_gerencia.comunicado_gerencia import ComunicadoGerencia


class DictRowComunicadoGerenciaAdapter:

    def __init__(self, row: DictRow):
        self.row = row

    def to_comunicado_gerencia(self) -> ComunicadoGerencia:
        return ComunicadoGerencia(
            id=self.row['id'],
            titulo=self.row['titulo'],
            descripcion=self.row['descripcion'],
            prioridad=self.row['prioridad'],
            fecha=self.row['fecha'],
            caducidad=self.row['caducidad'],
            nombre_gerente=self.row['nombre_gerente']
        )