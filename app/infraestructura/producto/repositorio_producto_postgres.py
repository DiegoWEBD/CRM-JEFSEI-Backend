from psycopg import sql

from app.dominio.producto.producto import Producto
from app.dominio.producto.repositorio_producto import RepositorioProducto
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioProductoPostgres(RepositorioProducto):

    def _construir_where(
        self,
        id_linea_negocio: int | None,
        texto_busqueda: str | None,
        params: dict,
    ) -> sql.Composable:
        condiciones: list[sql.Composable] = []

        condiciones.append(sql.SQL('eliminado = false'))

        if id_linea_negocio is not None:
            condiciones.append(sql.SQL('id_linea_negocio = %(id_linea_negocio)s'))
            params['id_linea_negocio'] = id_linea_negocio

        if texto_busqueda:
            condiciones.append(sql.SQL(
                'UNACCENT(LOWER(nombre)) LIKE UNACCENT(LOWER(%(texto_busqueda)s))'
            ))
            params['texto_busqueda'] = f'%{texto_busqueda}%'

        return sql.SQL(' WHERE ') + sql.SQL(' AND ').join(condiciones)

    def obtener_activos(
        self,
        id_linea_negocio: int | None = None,
        texto_busqueda: str | None = None,
        pagina: int = 1,
        tamano_pagina: int = 20,
    ) -> tuple[list[Producto], int]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                params: dict = {}
                where_clause = self._construir_where(id_linea_negocio, texto_busqueda, params)

                count_query = sql.SQL('SELECT COUNT(*) as total FROM Producto {where_clause}').format(
                    where_clause=where_clause,
                )
                cur.execute(count_query, params)
                total = cur.fetchone()['total'] # type: ignore

                offset = (pagina - 1) * tamano_pagina
                params['tamano_pagina'] = tamano_pagina
                params['offset'] = offset

                data_query = sql.SQL('''
                    SELECT id, nombre, id_linea_negocio, codigo
                    FROM Producto
                    {where_clause}
                    ORDER BY nombre
                    LIMIT %(tamano_pagina)s OFFSET %(offset)s
                ''').format(where_clause=where_clause)
                cur.execute(data_query, params)
                rows = cur.fetchall()

                productos = [
                    Producto(
                        id=row['id'],
                        nombre=row['nombre'],
                        id_linea_negocio=row['id_linea_negocio'],
                        codigo=row['codigo'],
                        eliminado=False,
                    )
                    for row in rows
                ]

                return productos, total

    def obtener_por_id(self, id: int) -> Producto | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select id, nombre, id_linea_negocio, codigo, eliminado
                    from Producto
                    where id = %(id)s and eliminado = false
                '''

                params = {'id': id}

                cur.execute(query, params)
                row = cur.fetchone()

                if not row:
                    return None

                return Producto(
                    id=row['id'],
                    nombre=row['nombre'],
                    id_linea_negocio=row['id_linea_negocio'],
                    codigo=row['codigo'],
                    eliminado=row['eliminado'],
                )

    def crear(self, producto: Producto) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    insert into Producto (nombre, id_linea_negocio, codigo, eliminado)
                    values (%(nombre)s, %(id_linea_negocio)s, %(codigo)s, %(eliminado)s)
                '''

                params = {
                    'nombre': producto.nombre,
                    'id_linea_negocio': producto.id_linea_negocio,
                    'codigo': producto.codigo,
                    'eliminado': producto.eliminado,
                }

                cur.execute(query, params)
                conn.commit()

                return True

    def actualizar(self, producto: Producto) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    update Producto
                    set nombre = %(nombre)s,
                        id_linea_negocio = %(id_linea_negocio)s,
                        codigo = %(codigo)s
                    where id = %(id)s and eliminado = false
                '''

                params = {
                    'id': producto.id,
                    'nombre': producto.nombre,
                    'id_linea_negocio': producto.id_linea_negocio,
                    'codigo': producto.codigo,
                }

                cur.execute(query, params)
                conn.commit()

                return cur.rowcount > 0

    def existe_por_nombre_y_linea_negocio(
        self, nombre: str, id_linea_negocio: int
    ) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    SELECT EXISTS(
                        SELECT 1 FROM Producto
                        WHERE UNACCENT(LOWER(nombre)) = UNACCENT(LOWER(%(nombre)s))
                        AND id_linea_negocio = %(id_linea_negocio)s
                        AND eliminado = false
                    ) as existe
                '''

                params = {
                    'nombre': nombre,
                    'id_linea_negocio': id_linea_negocio,
                }

                cur.execute(query, params)
                row = cur.fetchone()

                return row['existe']

    def eliminar(self, id: int) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    update Producto
                    set eliminado = true
                    where id = %(id)s and eliminado = false
                '''

                params = {'id': id}

                cur.execute(query, params)
                conn.commit()

                return cur.rowcount > 0
