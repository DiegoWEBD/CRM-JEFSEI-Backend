from psycopg.rows import DictRow

from app.dominio.auth.sesion_con_usuario import SesionConUsuario


class DictRowSesionAdapter:

    def __init__(self, row: DictRow) -> None:
        self._row = row

    def to_sesion_con_usuario(self) -> SesionConUsuario:
        return SesionConUsuario(
            id=self._row['id'],
            rut_usuario=self._row['rut_usuario'],
            nombre_usuario=self._row.get('nombre_usuario'),
            ip=self._row.get('ip'),
            user_agent=self._row.get('user_agent'),
            creado_en=self._row['creado_en'],
            expira_en=self._row['expira_en'],
            ultimo_acceso=self._row.get('ultimo_acceso'),
            revocado_en=self._row.get('revocado_en'),
            motivo_revocacion=self._row.get('motivo_revocacion'),
        )