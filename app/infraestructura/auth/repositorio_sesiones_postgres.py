from datetime import datetime
from uuid import UUID

from app.dominio.auth.sesion import Sesion
from app.dominio.auth.repositorio_sesiones import RepositorioSesiones
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioSesionesPostgres(RepositorioSesiones):

    def crear_sesion(
        self,
        rut_usuario: str,
        ip: str | None,
        user_agent: str | None,
        expira_en: datetime,
    ) -> UUID:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    INSERT INTO sesion (rut_usuario, ip, user_agent, expira_en)
                    VALUES (%(rut)s, %(ip)s, %(ua)s, %(exp)s)
                    RETURNING id
                    ''',
                    {'rut': rut_usuario, 'ip': ip, 'ua': user_agent, 'exp': expira_en},
                )
                return cur.fetchone()['id']

    def guardar_refresh_token(
        self,
        sesion_id: UUID,
        token_hash: str,
        expira_en: datetime,
    ) -> UUID:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    INSERT INTO refresh_token (sesion_id, token_hash, expira_en)
                    VALUES (%(sid)s, %(hash)s, %(exp)s)
                    RETURNING id
                    ''',
                    {'sid': sesion_id, 'hash': token_hash, 'exp': expira_en},
                )
                return cur.fetchone()['id']

    def obtener_sesion_viva(self, sesion_id: UUID) -> Sesion | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    SELECT id, rut_usuario, ip, user_agent, creado_en,
                           expira_en, ultimo_acceso, revocado_en, motivo_revocacion
                    FROM sesion
                    WHERE id = %(id)s
                      AND revocado_en IS NULL
                      AND expira_en > now()
                    ''',
                    {'id': sesion_id},
                )
                row = cur.fetchone()
                if row is None:
                    return None
                return Sesion(**row)

    def obtener_sesion_por_refresh_hash(
        self,
        token_hash: str,
    ) -> dict | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    SELECT rt.id AS token_id,
                           rt.usado_en AS token_usado_en,
                           rt.expira_en AS token_expira_en,
                           s.id AS sesion_id,
                           s.revocado_en AS sesion_revocado_en,
                           s.expira_en AS sesion_expira_en
                    FROM refresh_token rt
                    JOIN sesion s ON s.id = rt.sesion_id
                    WHERE rt.token_hash = %(hash)s
                    ''',
                    {'hash': token_hash},
                )
                return cur.fetchone()

    def marcar_refresh_usado(
        self,
        token_id: UUID,
        nuevo_token_id: UUID,
    ) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    UPDATE refresh_token
                    SET usado_en = now(), reemplazado_por = %(nuevo)s
                    WHERE id = %(id)s
                    ''',
                    {'id': token_id, 'nuevo': nuevo_token_id},
                )

    def actualizar_ultimo_acceso(self, sesion_id: UUID) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'UPDATE sesion SET ultimo_acceso = now() WHERE id = %(id)s',
                    {'id': sesion_id},
                )

    def revocar_sesion(self, sesion_id: UUID, motivo: str) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    UPDATE sesion
                    SET revocado_en = now(), motivo_revocacion = %(motivo)s
                    WHERE id = %(id)s AND revocado_en IS NULL
                    ''',
                    {'id': sesion_id, 'motivo': motivo},
                )

    def revocar_sesiones_usuario(self, rut: str, motivo: str) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    UPDATE sesion
                    SET revocado_en = now(), motivo_revocacion = %(motivo)s
                    WHERE rut_usuario = %(rut)s AND revocado_en IS NULL
                    ''',
                    {'rut': rut, 'motivo': motivo},
                )
