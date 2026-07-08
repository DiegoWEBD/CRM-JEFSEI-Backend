from psycopg.rows import DictRow

from app.dominio.usuario.usuario import Usuario
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.usuario.adaptadores.tuplerows_usuario_adapter import TupleRowsUsuarioAdapter

class RepositorioUsuariosPostgres(RepositorioUsuarios):

    def buscar(self, rut: str) -> Usuario | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select U.rut, U.nombre, 
                    U.correo, U.telefono,
                    U.meta_mensual_uf,
                    U.password_hash,
                    U.fecha_registro,
                    U.habilitado, U.eliminado,
                    U.porcentaje_comision,
                    S.id as id_sucursal,
                    S.nombre as nombre_sucursal, 
                    RU.codigo_rol,
                    R.nombre as rol,
                    PR.codigo_permiso, 
                    P.descripcion as descripcion_permiso
                    from Usuario U
                    inner join Sucursal S
                    on U.id_sucursal = S.id
                    left join RolUsuario RU
                    on U.rut = RU.rut_usuario
                    left join Rol R
                    on RU.codigo_rol = R.codigo
                    left join PermisoRol PR
                    on R.codigo = PR.codigo_rol
                    left join Permiso P
                    on PR.codigo_permiso = P.codigo
                    where U.rut = %(rut)s
                '''
                params = {
                    'rut': rut
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                if rows is None or len(rows) == 0:
                    return None

                return TupleRowsUsuarioAdapter(rows).to_usuario()
            
    def existe_correo(self, correo: str) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select correo
                    from Usuario
                    where correo = %(correo)s
                '''
                params = {
                    'correo': correo
                }

                cur.execute(query, params)
                row = cur.fetchone()

                return row is not None


    def existe_telefono(self, telefono: str) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select telefono
                    from Usuario
                    where telefono = %(telefono)s
                '''
                params = {
                    'telefono': telefono
                }

                cur.execute(query, params)
                row = cur.fetchone()

                return row is not None

            
    def obtener_todos(self) -> list[Usuario]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select U.rut, U.nombre, 
                    U.correo, U.telefono,
                    U.meta_mensual_uf,
                    U.password_hash,
                    U.fecha_registro,
                    U.habilitado, U.eliminado,
                    U.porcentaje_comision,
                    S.id as id_sucursal,
                    S.nombre as nombre_sucursal, 
                    RU.codigo_rol,
                    R.nombre as rol,
                    PR.codigo_permiso, 
                    P.descripcion as descripcion_permiso
                    from Usuario U
                    inner join Sucursal S
                    on U.id_sucursal = S.id
                    left join RolUsuario RU
                    on U.rut = RU.rut_usuario
                    left join Rol R
                    on RU.codigo_rol = R.codigo
                    left join PermisoRol PR
                    on R.codigo = PR.codigo_rol
                    left join Permiso P
                    on PR.codigo_permiso = P.codigo
                '''

                cur.execute(query)
                rows = cur.fetchall()

                if rows is None or len(rows) == 0:
                    return []

                datos_usuarios: dict[str, list[DictRow]] = {}

                for row in rows:
                    if row['rut'] not in datos_usuarios:
                        datos_usuarios[row['rut']] = []

                    datos_usuarios[row['rut']].append(row)

                usuarios: list[Usuario] = []

                for values in datos_usuarios.values():
                    usuarios.append(TupleRowsUsuarioAdapter(values).to_usuario())

                return usuarios

    def registrar(self, usuario: Usuario) -> bool:

        if not usuario.sucursal:
            return False

        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    insert into Usuario (rut, nombre, correo, telefono, id_sucursal, password_hash, meta_mensual_uf, porcentaje_comision)
                    values (%(rut)s, %(nombre)s, %(correo)s, %(telefono)s, %(id_sucursal)s, %(password_hash)s, %(meta_mensual_uf)s, %(porcentaje_comision)s)
                '''
                params = {
                    'rut': usuario.rut,
                    'nombre': usuario.nombre,
                    'correo': usuario.correo,
                    'telefono': usuario.telefono,
                    'id_sucursal': usuario.sucursal.id,
                    'password_hash': usuario.password_hash,
                    'meta_mensual_uf': usuario.meta_mensual_uf,
                    'porcentaje_comision': usuario.porcentaje_comision,
                }

                cur.execute(query, params)

                for rol in usuario.roles:
                    query = '''
                        insert into RolUsuario (rut_usuario, codigo_rol)
                        values (%(rut_usuario)s, %(codigo_rol)s)
                    '''

                    params = {
                        'rut_usuario': usuario.rut,
                        'codigo_rol': rol.codigo
                    }

                cur.execute(query, params)

                return True

    def eliminar(self, rut: str) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    update Usuario
                    set eliminado = true
                    where rut = %(rut)s
                '''
                params = {
                    'rut': rut
                }

                cur.execute(query, params)
                return cur.rowcount > 0
            
    def actualizar(self, usuario: Usuario) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    update Usuario
                    set nombre = %(nombre)s,
                        correo = %(correo)s,
                        telefono = %(telefono)s,
                        id_sucursal = %(id_sucursal)s,
                        password_hash = %(password_hash)s,
                        meta_mensual_uf = %(meta_mensual_uf)s,
                        porcentaje_comision = %(porcentaje_comision)s,
                        habilitado = %(habilitado)s
                    where rut = %(rut)s
                '''
                params = {
                    'rut': usuario.rut,
                    'nombre': usuario.nombre,
                    'correo': usuario.correo,
                    'telefono': usuario.telefono,
                    'id_sucursal': usuario.sucursal.id if usuario.sucursal else None,
                    'password_hash': usuario.password_hash,
                    'meta_mensual_uf': usuario.meta_mensual_uf,
                    'porcentaje_comision': usuario.porcentaje_comision,
                    'habilitado': usuario.habilitado
                }

                cur.execute(query, params)
                return True

    def asignar_roles(self, rut: str, codigo_roles: list[str]) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    delete from RolUsuario
                    where rut_usuario = %(rut_usuario)s
                '''
                params = {
                    'rut_usuario': rut
                }

                cur.execute(query, params)

                for codigo_rol in codigo_roles:
                    query = '''
                        insert into RolUsuario (rut_usuario, codigo_rol)
                        values (%(rut_usuario)s, %(codigo_rol)s)
                    '''

                    params = {
                        'rut_usuario': rut,
                        'codigo_rol': codigo_rol
                    }

                    cur.execute(query, params)

                return True