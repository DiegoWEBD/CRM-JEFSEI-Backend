import math
from typing import Optional

from psycopg import sql

from app.aplicacion.administrador_condominio.servicios.consulta_administradores_service import (
    ConsultaAdministradoresService,
)
from app.infraestructura.db.conexion import obtener_conexion


class ConsultaAdministradoresPostgresService(ConsultaAdministradoresService):

    _BASE_QUERY = sql.SQL('''
        SELECT 
            ac.id,
            ac.nombre_administrador,
            ac.nombre_contacto,
            ac.telefono,
            ac.correo,
            COUNT(pc.id) AS cantidad_condominios
        FROM AdministradorCondominio ac
        LEFT JOIN ProspectoCondominio pc ON pc.id_administrador = ac.id
        {where_clause}
        GROUP BY ac.id, ac.nombre_administrador, ac.nombre_contacto, ac.telefono, ac.correo
        ORDER BY ac.nombre_administrador
    ''')

    def _construir_where(
        self,
        texto_busqueda: Optional[str],
        params: dict,
    ) -> sql.Composable:
        condiciones: list[sql.Composable] = []

        if texto_busqueda:
            condiciones.append(sql.SQL('''
                (
                    UNACCENT(LOWER(ac.nombre_administrador)) LIKE UNACCENT(LOWER(%(texto_busqueda)s))
                    OR UNACCENT(LOWER(ac.nombre_contacto)) LIKE UNACCENT(LOWER(%(texto_busqueda)s))
                    OR UNACCENT(LOWER(ac.correo)) LIKE UNACCENT(LOWER(%(texto_busqueda)s))
                )
            '''))
            params["texto_busqueda"] = f"%{texto_busqueda}%"

        if condiciones:
            return sql.SQL(' WHERE ') + sql.SQL(' AND ').join(condiciones)
        return sql.SQL('')

    def obtener_todos(
        self,
        texto_busqueda: Optional[str] = None,
        pagina: int = 1,
        tamano_pagina: int = 25,
    ) -> dict:

        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                params: dict = {}
                where_clause = self._construir_where(texto_busqueda, params)

                count_query = sql.SQL('''
                    SELECT COUNT(DISTINCT ac.id) as total
                    FROM AdministradorCondominio ac
                    LEFT JOIN ProspectoCondominio pc ON pc.id_administrador = ac.id
                    {where_clause}
                ''').format(where_clause=where_clause)
                cur.execute(count_query, params)
                total = cur.fetchone()['total'] # type: ignore

                total_paginas = math.ceil(total / tamano_pagina) if total else 0

                offset = (pagina - 1) * tamano_pagina

                page_query = sql.SQL('''
                    SELECT 
                        ac.id,
                        ac.nombre_administrador,
                        ac.nombre_contacto,
                        ac.telefono,
                        ac.correo,
                        COUNT(pc.id) AS cantidad_condominios
                    FROM AdministradorCondominio ac
                    LEFT JOIN ProspectoCondominio pc ON pc.id_administrador = ac.id
                    {where_clause}
                    GROUP BY ac.id, ac.nombre_administrador, ac.nombre_contacto, ac.telefono, ac.correo
                    ORDER BY ac.nombre_administrador
                    LIMIT %(tamano_pagina)s OFFSET %(offset)s
                ''').format(where_clause=where_clause)
                page_params = {**params, "tamano_pagina": tamano_pagina, "offset": offset}
                cur.execute(page_query, page_params)
                rows = cur.fetchall()

                administradores = []
                if rows:
                    administradores = [
                        {
                            "id": row['id'],
                            "nombre_administrador": row['nombre_administrador'],
                            "nombre_contacto": row['nombre_contacto'],
                            "telefono": row['telefono'],
                            "correo": row['correo'],
                            "cantidad_condominios": row['cantidad_condominios'],
                        }
                        for row in rows
                    ]

                return {
                    'data': administradores,
                    'total': total,
                    'pagina': pagina,
                    'tamano_pagina': tamano_pagina,
                    'total_paginas': total_paginas,
                }
