from psycopg.rows import DictRow

from app.dominio.auditoria.registro_auditoria import RegistroAuditoria


class DictRowRegistroAuditoriaAdapter:

    def __init__(self, row: DictRow) -> None:
        self.row = row

    def to_registro_auditoria(self) -> RegistroAuditoria:
        return RegistroAuditoria(
            id=self.row['id'],
            categoria=self.row['categoria'],
            evento=self.row['evento'],
            resultado=self.row['resultado'],
            estado_http=self.row['estado_http'],
            rut_usuario=self.row['rut_usuario'],
            nombre_usuario=self.row['nombre_usuario'],
            ip_origen=self.row['ip_origen'],
            user_agent=self.row['user_agent'],
            id_peticion=self.row['id_peticion'],
            metodo=self.row['metodo'],
            ruta=self.row['ruta'],
            entidad_tipo=self.row['entidad_tipo'],
            entidad_id=self.row['entidad_id'],
            detalle=self.row['detalle'],
            duracion_ms=self.row['duracion_ms'],
            fecha_registro=self.row['fecha_registro'],
        )
