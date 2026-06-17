from app.dominio.authorization.authorizacion_repository import AuthorizationRepository
from app.infraestructura.db.conexion import obtener_conexion


class AuthorizationRepositoryPostgres(AuthorizationRepository):

    def usuario_puede_ver_solicitud_cotizacion(self, rut_usuario: str, id_solicitud: int) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select PC.rut_ej_comercial,
                    PC.rut_ej_evaluacion,
                    PC.rut_ej_renovacion,
                    PC.rut_as_renovacion
                    from SolicitudCotizacion SC
                    inner join ProcesoComercial PC
                    on SC.id_proceso_comercial = PC.id
                    where SC.id = %(id_solicitud)s
                '''

                params = {
                    'id_solicitud': id_solicitud
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    return False
                
                rut_ej_comercial = row['rut_ej_comercial']
                rut_ej_evaluacion = row['rut_ej_evaluacion']
                rut_ej_renovacion = row['rut_ej_renovacion']
                rut_as_renovacion = row['rut_as_renovacion']

                return any([
                    rut_ej_comercial == rut_usuario,
                    rut_ej_evaluacion == rut_usuario,
                    rut_ej_renovacion == rut_usuario,
                    rut_as_renovacion == rut_usuario
                ])
            
    def usuario_puede_gestionar_renovacion(self, rut_usuario: str, numero_poliza: str) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select C.rut_ej_renovacion_asignado,
                    C.rut_as_renovacion_asignado
                    from Poliza P
                    inner join Cliente C
                    on P.id_cliente = C.id
                    where P.numero_poliza = %(numero_poliza)s
                '''

                params = {
                    'numero_poliza': numero_poliza
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    return False
                
                rut_ej_renovacion_asignado = row['rut_ej_renovacion_asignado']
                rut_as_renovacion_asignado = row['rut_as_renovacion_asignado']

                return any([
                    rut_ej_renovacion_asignado == rut_usuario,
                    rut_as_renovacion_asignado == rut_usuario
                ])