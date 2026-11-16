from app.dominio.rol.rol import Rol
from app.dominio.rol.repositorio_roles import RepositorioRoles
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.rol.adaptadores.dictrow_rol_adapter import DictRowRolAdapter
from app.infraestructura.rol.adaptadores.rows_rol_con_permisos_adapter import RowsRolConPermisosAdapter


class RepositorioRolesPostgres(RepositorioRoles):

    def obtener_todos(self) -> list[Rol]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select codigo, nombre
                    from Rol
                    order by nombre
                '''

                cur.execute(query)
                rows = cur.fetchall()

                return [DictRowRolAdapter(row).to_rol() for row in rows]

    def obtener_por_codigo(self, codigo: str) -> Rol | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select codigo, nombre
                    from Rol
                    where codigo = %(codigo)s
                '''
                params = {
                    'codigo': codigo
                }

                cur.execute(query, params)
                row = cur.fetchone()

                return DictRowRolAdapter(row).to_rol() if row else None

    def obtener_con_permisos(self) -> list[Rol]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select R.codigo, R.nombre,
                           P.codigo as permiso_codigo,
                           P.descripcion as permiso_descripcion
                    from Rol R
                    left join PermisoRol PR on PR.codigo_rol = R.codigo
                    left join Permiso P on P.codigo = PR.codigo_permiso
                    order by R.nombre, P.codigo
                '''

                cur.execute(query)
                rows = cur.fetchall()

                return RowsRolConPermisosAdapter(rows).to_roles()

    def asignar_permisos(self, codigo_rol: str, codigos_permiso: list[str]) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    delete from PermisoRol
                    where codigo_rol = %(codigo_rol)s
                '''
                params = {
                    'codigo_rol': codigo_rol
                }

                cur.execute(query, params)

                for codigo_permiso in codigos_permiso:
                    query = '''
                        insert into PermisoRol (codigo_rol, codigo_permiso)
                        values (%(codigo_rol)s, %(codigo_permiso)s)
                    '''
                    params = {
                        'codigo_rol': codigo_rol,
                        'codigo_permiso': codigo_permiso
                    }

                    cur.execute(query, params)

                return True
