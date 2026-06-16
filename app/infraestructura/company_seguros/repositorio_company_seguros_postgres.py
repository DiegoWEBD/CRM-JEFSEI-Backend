from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.company_seguros.repositorio_company_seguros import RepositorioCompanySeguros
from app.dominio.factor_cuotas_company.factor_cuotas_company import FactorCuotasCompany
from app.infraestructura.company_seguros.adaptadores.tuplerows_company_seguros_adapter import TupleRowsCompanySegurosAdapter
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.factor_cuotas_company.adaptadores.dictrow_factor_cuotas_company_adapter import DictRowFactorCuotasCompanyAdapter


class RepositorioCompanySegurosPostgres(RepositorioCompanySeguros):
    
    def buscar(self, id: int) -> CompanySeguros | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select CS.id, CS.nombre, FCC.numero_cuotas, FCC.factor
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

    def obtener_factores_cuotas(self, id_company: int) -> list[FactorCuotasCompany]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select FCC.numero_cuotas, FCC.factor
                    from FactorCuotasCompany FCC
                    inner join CompanySeguros CS
                    on FCC.id_company = CS.id
                    where CS.id = %(id)s
                '''
                params = {
                    'id': id_company
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                if rows is None:
                    return []
                
                return [DictRowFactorCuotasCompanyAdapter(row).to_factor_cuotas_company() for row in rows]