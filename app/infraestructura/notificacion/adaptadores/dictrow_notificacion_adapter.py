from psycopg.rows import DictRow

from app.dominio.notificacion.notificacion import Notificacion


class DictRowNotificacionAdapter:

    def __init__(self, row: DictRow):
        self.row = row

    def to_notificacion(self) -> Notificacion:
        r = self.row
        return Notificacion(
            id=r['id'],
            rut_usuario=r['rut_usuario'],
            codigo_tipo=r['codigo_tipo'],
            nivel=r['nivel'],
            titulo=r['titulo'],
            mensaje=r['mensaje'],
            entidad_tipo=r['entidad_tipo'],
            entidad_id=r['entidad_id'],
            url_destino=r['url_destino'],
            dedupe_key=r['dedupe_key'],
            leida=r['leida'],
            fecha_leida=r['fecha_leida'],
            created_at=r['created_at'],
        )
