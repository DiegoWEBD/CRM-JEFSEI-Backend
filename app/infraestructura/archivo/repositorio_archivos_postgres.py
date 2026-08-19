from app.dominio.archivo.archivo import Archivo
from app.dominio.archivo.repositorio_archivos import RepositorioArchivos
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioArchivosPostgres(RepositorioArchivos):

    def insertar(
        self,
        id_prospecto: int,
        nombre_almacenado: str,
        nombre_original: str,
        tipo_contenido: str,
        tamano_bytes: int,
        rut_subido_por: str
    ) -> Archivo:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    insert into Archivo
                        (id_prospecto, nombre_almacenado, nombre_original,
                         tipo_contenido, tamano_bytes, rut_subido_por)
                    values
                        (%(id_prospecto)s, %(nombre_almacenado)s, %(nombre_original)s,
                         %(tipo_contenido)s, %(tamano_bytes)s, %(rut_subido_por)s)
                    returning id, created_at
                '''
                params = {
                    'id_prospecto': id_prospecto,
                    'nombre_almacenado': nombre_almacenado,
                    'nombre_original': nombre_original,
                    'tipo_contenido': tipo_contenido,
                    'tamano_bytes': tamano_bytes,
                    'rut_subido_por': rut_subido_por,
                }
                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    raise Exception('Error al registrar el archivo')

                return Archivo(
                    id=row['id'],
                    id_prospecto=id_prospecto,
                    nombre_almacenado=nombre_almacenado,
                    nombre_original=nombre_original,
                    tipo_contenido=tipo_contenido,
                    tamano_bytes=tamano_bytes,
                    rut_subido_por=rut_subido_por,
                    created_at=row['created_at'],
                )

    def listar_por_prospecto(self, id_prospecto: int) -> list[Archivo]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    select id, id_prospecto, nombre_almacenado, nombre_original,
                           tipo_contenido, tamano_bytes, rut_subido_por, created_at
                    from Archivo
                    where id_prospecto = %(id_prospecto)s
                    order by created_at desc
                '''
                params = {'id_prospecto': id_prospecto}
                cur.execute(query, params)
                rows = cur.fetchall()
                return [
                    Archivo(
                        id=row['id'],
                        id_prospecto=row['id_prospecto'],
                        nombre_almacenado=row['nombre_almacenado'],
                        nombre_original=row['nombre_original'],
                        tipo_contenido=row['tipo_contenido'],
                        tamano_bytes=row['tamano_bytes'],
                        rut_subido_por=row['rut_subido_por'],
                        created_at=row['created_at'],
                    )
                    for row in rows
                ]

    def obtener_por_id(self, id_archivo: int) -> Archivo | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    select id, id_prospecto, nombre_almacenado, nombre_original,
                           tipo_contenido, tamano_bytes, rut_subido_por, created_at
                    from Archivo
                    where id = %(id_archivo)s
                '''
                params = {'id_archivo': id_archivo}
                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    return None

                return Archivo(
                    id=row['id'],
                    id_prospecto=row['id_prospecto'],
                    nombre_almacenado=row['nombre_almacenado'],
                    nombre_original=row['nombre_original'],
                    tipo_contenido=row['tipo_contenido'],
                    tamano_bytes=row['tamano_bytes'],
                    rut_subido_por=row['rut_subido_por'],
                    created_at=row['created_at'],
                )

    def eliminar(self, id_archivo: int) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    delete from Archivo
                    where id = %(id_archivo)s
                    returning id
                '''
                params = {'id_archivo': id_archivo}
                cur.execute(query, params)
                row = cur.fetchone()
                return row is not None

    def existe_nombre_almacenado(self, id_prospecto: int, nombre_almacenado: str) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    select exists(
                        select 1 from Archivo
                        where id_prospecto = %(id_prospecto)s
                        and unaccent(lower(nombre_almacenado)) = unaccent(lower(%(nombre_almacenado)s))
                    )
                '''
                params = {
                    'id_prospecto': id_prospecto,
                    'nombre_almacenado': nombre_almacenado,
                }
                cur.execute(query, params)
                row = cur.fetchone()
                return row['exists'] # type: ignore
