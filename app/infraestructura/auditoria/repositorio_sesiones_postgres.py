from datetime import datetime
from typing import Optional

from psycopg import Connection
from psycopg.rows import DictRow

from app.dominio.auditoria.repositorio_sesiones import RepositorioSesiones
from app.dominio.auditoria.sesion import Sesion
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioSesionesPostgres(RepositorioSesiones):

    def crear(self, sesion: Sesion, conn: Optional[Connection[DictRow]] = None) -> Sesion:
        query = '''
            insert into Sesion (
                id, rut_usuario, fecha_creacion, fecha_expiracion,
                fecha_ultimo_uso, ip_origen, user_agent, device_id
            ) values (
                %(id)s, %(rut_usuario)s, coalesce(%(fecha_creacion)s, current_timestamp),
                %(fecha_expiracion)s, %(fecha_ultimo_uso)s,
                %(ip_origen)s::inet, %(user_agent)s, %(device_id)s
            )
            returning id
        '''
        params = {
            'id': sesion.id,
            'rut_usuario': sesion.rut_usuario,
            'fecha_creacion': sesion.fecha_creacion,
            'fecha_expiracion': sesion.fecha_expiracion,
            'fecha_ultimo_uso': sesion.fecha_ultimo_uso,
            'ip_origen': sesion.ip_origen,
            'user_agent': sesion.user_agent,
            'device_id': sesion.device_id,
        }
        with _ejecutar(conn) as cur:
            cur.execute(query, params)
        return sesion

    def obtener_por_id(
        self,
        id_sesion: str,
        conn: Optional[Connection[DictRow]] = None,
    ) -> Sesion | None:
        query = '''
            select id, rut_usuario, fecha_creacion, fecha_expiracion,
                   fecha_ultimo_uso, revocada, fecha_revocacion,
                   motivo_revocacion, ip_origen, user_agent, device_id
            from Sesion
            where id = %(id_sesion)s
        '''
        with _ejecutar(conn) as cur:
            cur.execute(query, {'id_sesion': id_sesion})
            fila = cur.fetchone()
        return _a_sesion(fila) if fila else None

    def revocar(
        self,
        id_sesion: str,
        motivo: str,
        conn: Optional[Connection[DictRow]] = None,
    ) -> None:
        query = '''
            update Sesion
            set revocada = true,
                fecha_revocacion = current_timestamp,
                motivo_revocacion = %(motivo)s
            where id = %(id_sesion)s and revocada = false
        '''
        with _ejecutar(conn) as cur:
            cur.execute(query, {'id_sesion': id_sesion, 'motivo': motivo})

    def revocar_todas_del_usuario(
        self,
        rut_usuario: str,
        motivo: str,
        conn: Optional[Connection[DictRow]] = None,
    ) -> int:
        with _ejecutar(conn) as cur:
            cur.execute('''
                update Sesion
                set revocada = true,
                    fecha_revocacion = current_timestamp,
                    motivo_revocacion = %(motivo)s
                where rut_usuario = %(rut_usuario)s and revocada = false
            ''', {'rut_usuario': rut_usuario, 'motivo': motivo})
            return cur.rowcount

    def registrar_uso(
        self,
        id_sesion: str,
        conn: Optional[Connection[DictRow]] = None,
    ) -> None:
        with _ejecutar(conn) as cur:
            cur.execute(
                'update Sesion set fecha_ultimo_uso = current_timestamp where id = %(id)s',
                {'id': id_sesion},
            )

    # --- Refresh tokens ---

    def crear_refresh_token(
        self,
        id_sesion: str,
        token_hash: str,
        fecha_expiracion: datetime,
        conn: Optional[Connection[DictRow]] = None,
    ) -> str:
        with _ejecutar(conn) as cur:
            cur.execute('''
                insert into RefreshToken (
                    id_sesion, token_hash, fecha_expiracion
                ) values (
                    %(id_sesion)s, %(token_hash)s, %(fecha_expiracion)s
                )
                returning id
            ''', {
                'id_sesion': id_sesion,
                'token_hash': token_hash,
                'fecha_expiracion': fecha_expiracion,
            })
            fila = cur.fetchone()
        return str(fila['id'])

    def obtener_refresh_token_por_hash(
        self,
        token_hash: str,
        conn: Optional[Connection[DictRow]] = None,
    ) -> dict | None:
        with _ejecutar(conn) as cur:
            cur.execute('''
                select id, id_sesion, fecha_creacion, fecha_expiracion,
                       revocado, usado, fecha_uso
                from RefreshToken
                where token_hash = %(token_hash)s
            ''', {'token_hash': token_hash})
            fila = cur.fetchone()
        return dict(fila) if fila else None

    def marcar_refresh_token_usado(
        self,
        id_refresh_token: str,
        conn: Optional[Connection[DictRow]] = None,
    ) -> None:
        with _ejecutar(conn) as cur:
            cur.execute('''
                update RefreshToken
                set usado = true, revocado = true, fecha_uso = current_timestamp
                where id = %(id)s
            ''', {'id': id_refresh_token})

    def revocar_refresh_tokens_de_sesion(
        self,
        id_sesion: str,
        conn: Optional[Connection[DictRow]] = None,
    ) -> None:
        with _ejecutar(conn) as cur:
            cur.execute('''
                update RefreshToken
                set revocado = true
                where id_sesion = %(id_sesion)s and revocado = false
            ''', {'id_sesion': id_sesion})

    def revocar_refresh_tokens_older_than(
        self,
        id_sesion: str,
        id_refresh_token: str,
        conn: Optional[Connection[DictRow]] = None,
    ) -> int:
        """Deja activo sólo un refresh token por sesión.

        Es la defesa real contra la reutilización: si un token viejo se presenta
        fuera de la ventana de gracia, ya no sirve para nada porque fue revocado
        en su momento.
        """
        with _ejecutar(conn) as cur:
            cur.execute('''
                update RefreshToken
                set revocado = true
                where id_sesion = %(id_sesion)s
                  and id <> %(id_refresh_token)s
                  and revocado = false
            ''', {'id_sesion': id_sesion, 'id_refresh_token': id_refresh_token})
            return cur.rowcount


class _Ejecucion:
    """Cursor sobre la conexión del UoW, o conexión propia si no hay UoW.

    Cuando la conexión es propia se hace commit explícito al salir limpio:
    cerrarla sin commit haría rollback y las escrituras se perderían. Con
    conexión de UoW no se confirma nada: el commit es responsabilidad de la
    unidad de trabajo, que abarca la transacción completa del caso de uso.
    """

    def __init__(self, conn: Optional[Connection[DictRow]]):
        self._propia = conn is None
        self._conexion = obtener_conexion() if self._propia else conn
        self._cursor = None

    def __enter__(self):
        self._cursor = self._conexion.cursor()
        return self._cursor

    def __exit__(self, tipo_exc, exc, tb):
        try:
            if self._propia:
                if tipo_exc is None:
                    self._conexion.commit()
                else:
                    self._conexion.rollback()
        finally:
            if self._propia:
                self._conexion.close()
        return False


def _ejecutar(conn):
    return _Ejecucion(conn)


def _a_sesion(fila: DictRow) -> Sesion:
    return Sesion(
        id=str(fila['id']),
        rut_usuario=fila['rut_usuario'],
        fecha_creacion=fila['fecha_creacion'],
        fecha_expiracion=fila['fecha_expiracion'],
        fecha_ultimo_uso=fila['fecha_ultimo_uso'],
        revocada=fila['revocada'],
        fecha_revocacion=fila['fecha_revocacion'],
        motivo_revocacion=fila['motivo_revocacion'],
        ip_origen=str(fila['ip_origen']) if fila['ip_origen'] else None,
        user_agent=fila['user_agent'],
        device_id=str(fila['device_id']) if fila['device_id'] else None,
    )
