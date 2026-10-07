from datetime import datetime
from uuid import UUID

from psycopg import sql
from psycopg.rows import DictRow

from app.dominio.auth.sesion import Sesion
from app.dominio.auth.repositorio_sesiones import RepositorioSesiones
from app.dominio.auth.sesion_con_usuario import SesionConUsuario
from app.infraestructura.auth.adaptadores.dictrow_sesion_adapter import (
    DictRowSesionAdapter,
)
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

    # ── Consulta paginada para administración ──────────────────

    def _construir_where_sesiones(
        self,
        texto_busqueda: str | None,
        rut_usuario: str | None,
        estado: str | None,
        params: dict[str, object],
    ) -> sql.Composed:
        condiciones: list[sql.Composed] = []

        if texto_busqueda:
            condiciones.append(sql.SQL(
                '('
                'UNACCENT(LOWER(s.ip)) LIKE UNACCENT(LOWER(%(texto_busqueda)s)) '
                'OR UNACCENT(LOWER(s.rut_usuario)) LIKE UNACCENT(LOWER(%(texto_busqueda)s)) '
                'OR UNACCENT(LOWER(u.nombre)) LIKE UNACCENT(LOWER(%(texto_busqueda)s))'
                ')'
            ))
            params['texto_busqueda'] = f'%{texto_busqueda}%'

        if rut_usuario:
            condiciones.append(sql.SQL('s.rut_usuario = %(rut_usuario)s'))
            params['rut_usuario'] = rut_usuario

        if estado == 'activas':
            condiciones.append(sql.SQL(
                's.revocado_en IS NULL AND s.expira_en > now()'
            ))
        elif estado == 'inactivas':
            condiciones.append(sql.SQL(
                '(s.revocado_en IS NOT NULL OR s.expira_en <= now())'
            ))
        # 'todas' o None → sin filtro de estado

        if not condiciones:
            return sql.SQL('')

        return sql.SQL(' WHERE ') + sql.SQL(' AND ').join(condiciones)

    def obtener_sesiones_paginadas(
        self,
        texto_busqueda: str | None,
        rut_usuario: str | None,
        estado: str | None,
        pagina: int,
        tamano_pagina: int,
    ) -> tuple[list[SesionConUsuario], int]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                params: dict[str, object] = {}
                where_clause = self._construir_where_sesiones(
                    texto_busqueda, rut_usuario, estado, params,
                )

                count_query = sql.SQL('''
                    SELECT COUNT(*) AS total
                    FROM sesion s
                    LEFT JOIN usuario u ON u.rut = s.rut_usuario
                    {where_clause}
                ''').format(where_clause=where_clause)
                cur.execute(count_query, params)
                total: int = cur.fetchone()['total']  # type: ignore[assignment]

                offset = (pagina - 1) * tamano_pagina

                data_query = sql.SQL('''
                    SELECT
                        s.id, s.rut_usuario, u.nombre AS nombre_usuario,
                        s.ip, s.user_agent, s.creado_en, s.expira_en,
                        s.ultimo_acceso, s.revocado_en, s.motivo_revocacion
                    FROM sesion s
                    LEFT JOIN usuario u ON u.rut = s.rut_usuario
                    {where_clause}
                    ORDER BY s.creado_en DESC
                    LIMIT %(tamano_pagina)s OFFSET %(offset)s
                ''').format(where_clause=where_clause)
                page_params: dict[str, object] = {
                    **params,
                    'tamano_pagina': tamano_pagina,
                    'offset': offset,
                }
                cur.execute(data_query, page_params)
                rows: list[DictRow] = cur.fetchall()  # type: ignore[assignment]

                sesiones = [
                    DictRowSesionAdapter(row).to_sesion_con_usuario()
                    for row in rows
                ]

                return sesiones, total
