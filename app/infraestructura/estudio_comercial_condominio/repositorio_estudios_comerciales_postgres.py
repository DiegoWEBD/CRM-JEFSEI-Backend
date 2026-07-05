from app.dominio.estudio_comercial.estudio_comercial_condominio.estudio_comercial_condominio import EstudioComercialCondominio
from app.dominio.estudio_comercial.estudio_comercial_condominio.repositorio_estudios_comerciales import RepositorioEstudiosComerciales
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioEstudiosComercialesPostgres(RepositorioEstudiosComerciales):

    def insertar(
        self,
        id_solicitud: int,
        nombre_archivo: str
    ) -> int:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    insert into EstudioComercialCondominio (id_solicitud, nombre_archivo)
                    values (%(id_solicitud)s, %(nombre_archivo)s)
                    returning id
                '''
                params = {
                    'id_solicitud': id_solicitud,
                    'nombre_archivo': nombre_archivo,
                }
                cur.execute(query, params)
                row = cur.fetchone()
                if row is None:
                    raise Exception('Error al registrar el estudio comercial')
                return row['id']

    def listar_por_id_solicitud(
        self,
        id_solicitud: int
    ) -> list[EstudioComercialCondominio]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    select id, id_solicitud, nombre_archivo
                    from EstudioComercialCondominio
                    where id_solicitud = %(id_solicitud)s
                    order by id desc
                '''
                params = {'id_solicitud': id_solicitud}
                cur.execute(query, params)
                rows = cur.fetchall()
                return [
                    EstudioComercialCondominio(
                        id=row['id'],
                        id_solicitud=row['id_solicitud'],
                        nombre_archivo=row['nombre_archivo'],
                    )
                    for row in rows
                ]
