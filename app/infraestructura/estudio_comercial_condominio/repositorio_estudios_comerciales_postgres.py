from datetime import datetime

from app.dominio.estudio_comercial.estudio_comercial_condominio.estudio_comercial_condominio import EstudioComercialCondominio
from app.dominio.estudio_comercial.estudio_comercial_condominio.repositorio_estudios_comerciales import RepositorioEstudiosComerciales
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioEstudiosComercialesPostgres(RepositorioEstudiosComerciales):

    def insertar(
        self,
        id_solicitud: int,
        nombre_archivo: str,
        rut_usuario: str
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
                
                id_estudio = row['id']

                # Registro de historial

                query = '''
                    select SC.id_proceso_comercial
                    from EstudioComercialCondominio EC
                    inner join SolicitudCotizacion SC
                    on EC.id_solicitud = SC.id
                    where id_solicitud = %(id_solicitud)s
                '''

                params = {
                    'id_solicitud': id_solicitud
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    raise Exception('Error al registrar el estudio comercial')
                
                id_proceso_comercial = row['id_proceso_comercial']

                query = '''
                    insert into HistorialEstadoInformativoProcesoComercial(
                        id_proceso_comercial, 
                        codigo_estado, 
                        fecha_registro,
                        observacion,
                        rut_registrado_por
                    )
                    values(
                        %(id_proceso_comercial)s, 
                        %(codigo_estado)s, 
                        %(fecha_registro)s,
                        %(observacion)s,
                        %(rut_registrado_por)s
                    )
                '''

                params = {
                    'id_proceso_comercial': id_proceso_comercial,
                    'codigo_estado': 'ESTUDIO_DISPONIBLE',
                    'fecha_registro': datetime.now(),
                    'observacion': None,
                    'rut_registrado_por': rut_usuario
                }

                cur.execute(query, params)

                return id_estudio

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
