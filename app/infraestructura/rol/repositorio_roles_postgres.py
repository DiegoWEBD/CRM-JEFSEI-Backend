from app.dominio.rol.rol import Rol
from app.dominio.rol.repositorio_roles import RepositorioRoles
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.rol.adaptadores.dictrow_rol_adapter import DictRowRolAdapter


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
