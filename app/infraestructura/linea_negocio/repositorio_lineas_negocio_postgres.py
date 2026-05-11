from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.linea_negocio.repositorio_lineas_negocio import RepositorioLineasNegocio
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.linea_negocio.adaptadores.tuplerows_lineas_negocio_adapter import TupleRowsLineasNegocioAdapter


class RepositorioLineasNegocioPostgres(RepositorioLineasNegocio):

    def obtener_todas(self) -> list[LineaNegocio]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select LN.id as id_linea_negocio,
                    LN.nombre as nombre_linea_negocio,
                    P.id as id_producto, P.nombre as nombre_producto
                    from LineaNegocio LN
                    left join Producto P
                    on LN.id = P.id_linea_negocio
                '''

                cur.execute(query)
                rows = cur.fetchall()

                if rows is None or len(rows) == 0:
                    return None

                return TupleRowsLineasNegocioAdapter(rows).to_lineas_negocio()