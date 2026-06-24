from app.dominio.authorization.authorizacion_repository import AuthorizationRepository
from app.infraestructura.db.conexion import obtener_conexion


class AuthorizationRepositoryPostgres(AuthorizationRepository):

    def usuario_puede_ver_prospecto(self, rut_usuario: str, id_prospecto) -> bool:
         with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select PR.codigo_permiso
                    from Usuario U
                    inner join RolUsuario RU
                    on U.rut = RU.rut_usuario
                    inner join PermisoRol PR
                    on RU.codigo_rol = PR.codigo_rol
                    where U.rut = %(rut_usuario)s
                '''

                params = {
                    'rut_usuario': rut_usuario
                }

                cur.execute(query, params)
                rows = cur.fetchall()
                tiene_permisos = False

                for row in rows:
                    if row['codigo_permiso'] == 'OBTENER_PROSPECTOS_TODOS':
                        return True
                    if row['codigo_permiso'] == 'OBTENER_PROSPECTOS_PROPIOS':
                        tiene_permisos = True

                if not tiene_permisos:
                    return False

                query = '''
                    select rut_registrado_por,
                    rut_ej_comercial_asignado,
                    rut_ej_evaluacion_asignado
                    from Prospecto
                    where id = %(id_prospecto)s
                '''

                params = {
                    'id_prospecto': id_prospecto
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    return False

                autorizado = any([
                    row['rut_registrado_por'] == rut_usuario,
                    row['rut_ej_comercial_asignado'] == rut_usuario,
                    row['rut_ej_evaluacion_asignado'] == rut_usuario
                ])

                if autorizado:
                    return True
                
                query = '''
                    select id,
                    rut_ej_renovacion_asignado, 
                    rut_as_renovacion_asignado
                    from Cliente
                    where id_prospecto = %(id_prospecto)s
                '''

                params = {
                    'id_prospecto': id_prospecto
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    return False

                return any([
                    row['rut_ej_renovacion_asignado'] == rut_usuario,
                    row['rut_as_renovacion_asignado'] == rut_usuario
                ])

    def usuario_puede_ver_solicitud_cotizacion(self, rut_usuario: str, id_solicitud: int) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select PR.codigo_permiso
                    from Usuario U
                    inner join RolUsuario RU
                    on U.rut = RU.rut_usuario
                    inner join PermisoRol PR
                    on RU.codigo_rol = PR.codigo_rol
                    where U.rut = %(rut_usuario)s
                '''

                params = {
                    'rut_usuario': rut_usuario
                }

                cur.execute(query, params)
                rows = cur.fetchall()
                tiene_permisos = False

                for row in rows:
                    if row['codigo_permiso'] == 'VER_SOLICITUDES_COTIZACION_GLOBAL':
                        return True
                    if row['codigo_permiso'] == 'VER_SOLICITUDES_COTIZACION_PROPIAS':
                        tiene_permisos = True

                if not tiene_permisos:
                    return False

                query = '''
                    select P.rut_ej_comercial_asignado,
                    P.rut_ej_evaluacion_asignado
                    from SolicitudCotizacion SC
                    inner join ProcesoComercial PC
                    on SC.id_proceso_comercial = PC.id
                    inner join Prospecto P
                    on PC.id_prospecto = P.id
                    where SC.id = %(id_solicitud)s
                '''

                params = {
                    'id_solicitud': id_solicitud
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    return False

                return any([
                    row['rut_ej_comercial_asignado'] == rut_usuario,
                    row['rut_ej_evaluacion_asignado'] == rut_usuario
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
            
    def usuario_puede_crear_proceso_comercial(self, rut_usuario: str, id_prospecto: int) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select PR.codigo_permiso
                    from Usuario U
                    inner join RolUsuario RU
                    on U.rut = RU.rut_usuario
                    inner join PermisoRol PR
                    on RU.codigo_rol = PR.codigo_rol
                    where U.rut = %(rut_usuario)s
                '''

                params = {
                    'rut_usuario': rut_usuario
                }

                cur.execute(query, params)
                rows = cur.fetchall()
                tiene_permisos = False

                for row in rows:
                    if row['codigo_permiso'] == 'ADMINISTRAR_PROCESOS_COMERCIALES':
                        return True
                    if row['codigo_permiso'] == 'ADMINISTRAR_PROCESOS_COMERCIALES_PROPIOS':
                        tiene_permisos = True

                if not tiene_permisos:
                    return False

                query = '''
                    select rut_ej_comercial_asignado
                    from Prospecto
                    where id = %(id_prospecto)s
                '''

                params = {
                    'id_prospecto': id_prospecto
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    return False
                
                rut_ej_comercial_asignado = row['rut_ej_comercial_asignado']

                return any([
                    rut_ej_comercial_asignado == rut_usuario
                ])
            
    def usuario_puede_solicitar_cotizacion(self, rut_usuario: str, id_proceso_comercial: int) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select PR.codigo_permiso
                    from Usuario U
                    inner join RolUsuario RU
                    on U.rut = RU.rut_usuario
                    inner join PermisoRol PR
                    on RU.codigo_rol = PR.codigo_rol
                    where U.rut = %(rut_usuario)s
                '''

                params = {
                    'rut_usuario': rut_usuario
                }

                cur.execute(query, params)
                rows = cur.fetchall()
                tiene_permisos = False

                for row in rows:
                    if row['codigo_permiso'] == 'SOLICITAR_COTIZACION':
                        tiene_permisos = True
                        break

                if not tiene_permisos:
                    return False

                query = '''
                    select P.rut_ej_comercial_asignado
                    from ProcesoComercial PC 
                    inner join Prospecto P
                    on PC.id_prospecto = P.id
                    where PC.id = %(id_proceso_comercial)s
                '''

                params = {
                    'id_proceso_comercial':id_proceso_comercial
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    return False

                return row['rut_ej_comercial_asignado'] == rut_usuario

    def usuario_puede_ver_procesos_comerciales(self, rut_usuario: str, id_prospecto: int) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select PR.codigo_permiso
                    from Usuario U
                    inner join RolUsuario RU
                    on U.rut = RU.rut_usuario
                    inner join PermisoRol PR
                    on RU.codigo_rol = PR.codigo_rol
                    where U.rut = %(rut_usuario)s
                '''

                params = {
                    'rut_usuario': rut_usuario
                }

                cur.execute(query, params)
                rows = cur.fetchall()
                tiene_permisos = False

                for row in rows:
                    if row['codigo_permiso'] == 'ADMINISTRAR_PROCESOS_COMERCIALES':
                        return True
                    if row['codigo_permiso'] == 'ADMINISTRAR_PROCESOS_COMERCIALES_PROPIOS':
                        tiene_permisos = True

                if not tiene_permisos:
                    return False

                query = '''
                    select rut_registrado_por,
                    rut_ej_comercial_asignado,
                    rut_ej_evaluacion_asignado
                    from Prospecto
                    where id = %(id_prospecto)s
                '''

                params = {
                    'id_prospecto': id_prospecto
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    return False

                return any([
                    row['rut_registrado_por'] == rut_usuario,
                    row['rut_ej_comercial_asignado'] == rut_usuario,
                    row['rut_ej_evaluacion_asignado'] == rut_usuario
                ])

            
    def usuario_puede_subir_poliza(self, rut_usuario: str, id_proceso_comercial: int) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select PR.codigo_permiso
                    from Usuario U
                    inner join RolUsuario RU
                    on U.rut = RU.rut_usuario
                    inner join PermisoRol PR
                    on RU.codigo_rol = PR.codigo_rol
                    where U.rut = %(rut_usuario)s
                '''

                params = {
                    'rut_usuario': rut_usuario
                }

                cur.execute(query, params)
                rows = cur.fetchall()
                tiene_permisos = False

                for row in rows:
                    if row['codigo_permiso'] == 'CARGAR_POLIZAS_GLOBAL':
                        return True
                    if row['codigo_permiso'] == 'CARGAR_POLIZAS_PROPIAS':
                        tiene_permisos = True

                if not tiene_permisos:
                    return False

                query = '''
                    select P.rut_ej_comercial_asignado
                    from ProcesoComercial PC 
                    inner join Prospecto P
                    on PC.id_prospecto = P.id
                    where PC.id = %(id_proceso_comercial)s
                '''

                params = {
                    'id_proceso_comercial':id_proceso_comercial
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    return False

                return row['rut_ej_comercial_asignado'] == rut_usuario