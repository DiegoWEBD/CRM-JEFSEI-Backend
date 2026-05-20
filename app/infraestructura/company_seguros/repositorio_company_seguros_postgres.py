from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.company_seguros.repositorio_company_seguros import RepositorioCompanySeguros
from app.infraestructura.company_seguros.adaptadores.tuplerows_company_seguros_adapter import TupleRowsCompanySegurosAdapter
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioCompanySegurosPostgres(RepositorioCompanySeguros):
    
    def buscar(self, id: int) -> CompanySeguros | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select CS.id, CS.nombre, CS.nombre_logo, FCC.numero_cuotas, FCC.factor
                    from CompanySeguros CS
                    left join FactorCuotasCompany FCC
                    on CS.id = FCC.id_company
                    where CS.id = %(id)s
                '''
                params = {
                    'id': id
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                if not rows or len(rows) == 0:
                    return None
                
                return TupleRowsCompanySegurosAdapter(rows).to_company_seguros()
