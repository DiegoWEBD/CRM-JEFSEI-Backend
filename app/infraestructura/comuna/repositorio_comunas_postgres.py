from app.dominio.comuna.comuna import Comuna
from app.dominio.comuna.repositorio_comunas import RepositorioComunas
from app.infraestructura.comuna.adaptadores.tuplerow_comuna_adapter import TupleRowComunaAdapter
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioComunasPostgres(RepositorioComunas):

    def obtener_todas(self) -> list[Comuna]:
        
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select id, nombre
                    from Comuna
                '''

                cur.execute(query)
                rows = cur.fetchall()

                if rows is None or len(rows) == 0:
                    return []

                return [TupleRowComunaAdapter(row).to_comuna() for row in rows]