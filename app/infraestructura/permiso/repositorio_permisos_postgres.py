from app.dominio.permiso.permiso import Permiso
from app.dominio.permiso.repositorio_permisos import RepositorioPermisos
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.permiso.adaptadores.dictrow_permiso_adapter import DictRowPermisoAdapter


class RepositorioPermisosPostgres(RepositorioPermisos):

    def obtener_todos(self) -> list[Permiso]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select codigo, descripcion, nombre
                    from Permiso
                    order by codigo
                '''

                cur.execute(query)
                rows = cur.fetchall()

                return [DictRowPermisoAdapter(row).to_permiso() for row in rows]

    def obtener_por_codigos(self, codigos: list[str]) -> list[Permiso]:
        if not codigos:
            return []

        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select codigo, descripcion, nombre
                    from Permiso
                    where codigo = any(%(codigos)s)
                '''
                params = {
                    'codigos': codigos
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                return [DictRowPermisoAdapter(row).to_permiso() for row in rows]
