from app.dominio.sucursal.repositorio_sucursales import RepositorioSucursales
from app.dominio.sucursal.sucursal import Sucursal
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.sucursal.adaptadores.dictrow_sucursal_adapter import DictRowSucursalAdapter


class RepositorioSucursalesPostgres(RepositorioSucursales):

    def obtener_sucursales(self) -> list[Sucursal]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    select id, nombre
                    from Sucursal
                '''

                cur.execute(query)
                rows = cur.fetchall()

                return [DictRowSucursalAdapter(row).to_sucursal() for row in rows]