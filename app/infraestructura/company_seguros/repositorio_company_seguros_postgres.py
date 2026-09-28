from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.company_seguros.repositorio_company_seguros import RepositorioCompanySeguros
from app.dominio.factor_cuotas_company.factor_cuotas_company import FactorCuotasCompany
from app.infraestructura.company_seguros.adaptadores.tuplerow_company_seguros_resumen_adapter import TupleRowCompanySegurosResumenAdapter
from app.infraestructura.company_seguros.adaptadores.tuplerows_company_seguros_adapter import TupleRowsCompanySegurosAdapter
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.factor_cuotas_company.adaptadores.dictrow_factor_cuotas_company_adapter import DictRowFactorCuotasCompanyAdapter


class RepositorioCompanySegurosPostgres(RepositorioCompanySeguros):
    
    def obtener_todas(self) -> list[CompanySeguros]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select id, nombre
                    from CompanySeguros
                    where eliminado = false
                    order by nombre
                '''

                cur.execute(query)
                rows = cur.fetchall()

                if not rows:
                    return []

                return [TupleRowCompanySegurosResumenAdapter(row).to_company_seguros() for row in rows]

    def buscar(self, id: int) -> CompanySeguros | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select CS.id, CS.nombre, FCC.numero_cuotas, FCC.factor
                    from CompanySeguros CS
                    left join FactorCuotasCompany FCC
                    on CS.id = FCC.id_company
                    where CS.id = %(id)s and CS.eliminado = false
                '''
                params = {
                    'id': id
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                if not rows or len(rows) == 0:
                    return None
                
                return TupleRowsCompanySegurosAdapter(rows).to_company_seguros()

    def obtener_paginadas(
        self,
        texto_busqueda: str | None = None,
        pagina: int = 1,
        tamano_pagina: int = 15,
    ) -> tuple[list[CompanySeguros], int]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                condiciones: list[str] = ['eliminado = false']
                params: dict = {}

                if texto_busqueda:
                    condiciones.append(
                        'UNACCENT(LOWER(nombre)) LIKE UNACCENT(LOWER(%(texto_busqueda)s))'
                    )
                    params['texto_busqueda'] = f'%{texto_busqueda.strip().lower()}%'

                where_clause = ' and '.join(condiciones)

                count_query = f'select count(*) as total from CompanySeguros where {where_clause}'
                cur.execute(count_query, params)
                total = cur.fetchone()['total']

                offset = (pagina - 1) * tamano_pagina
                params['tamano_pagina'] = tamano_pagina
                params['offset'] = offset

                data_query = f'''
                    select id, nombre
                    from CompanySeguros
                    where {where_clause}
                    order by nombre
                    limit %(tamano_pagina)s offset %(offset)s
                '''
                cur.execute(data_query, params)
                rows = cur.fetchall()

                if not rows:
                    return [], total

                companies = [TupleRowCompanySegurosResumenAdapter(row).to_company_seguros() for row in rows]

                ids = [company.id for company in companies]

                factores_query = '''
                    select id_company, numero_cuotas, factor
                    from FactorCuotasCompany
                    where id_company = any(%(ids)s)
                    order by numero_cuotas asc
                '''
                cur.execute(factores_query, {'ids': ids})
                factores_rows = cur.fetchall()

                factores_por_company: dict[int, list[FactorCuotasCompany]] = {}
                for row in factores_rows:
                    factores_por_company.setdefault(row['id_company'], []).append(
                        FactorCuotasCompany(
                            numero_cuotas=row['numero_cuotas'],
                            factor=row['factor'],
                        )
                    )

                for company in companies:
                    company.factores_cuotas = factores_por_company.get(company.id, [])

                return companies, total

    def obtener_factores_cuotas(self, id_company: int) -> list[FactorCuotasCompany]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select FCC.numero_cuotas, FCC.factor
                    from FactorCuotasCompany FCC
                    inner join CompanySeguros CS
                    on FCC.id_company = CS.id
                    where CS.id = %(id)s and CS.eliminado = false
                    order by FCC.numero_cuotas asc
                '''
                params = {
                    'id': id_company
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                if rows is None:
                    return []
                
                return [DictRowFactorCuotasCompanyAdapter(row).to_factor_cuotas_company() for row in rows]

    def existe_por_nombre(self, nombre: str, id_excluir: int | None = None) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    SELECT EXISTS(
                        SELECT 1 FROM CompanySeguros
                        WHERE UNACCENT(LOWER(nombre)) = UNACCENT(LOWER(%(nombre)s))
                        AND eliminado = false
                '''
                params: dict = {
                    'nombre': nombre.strip().lower(),
                }

                if id_excluir is not None:
                    query += '''
                        AND id <> %(id_excluir)s
                    '''
                    params['id_excluir'] = id_excluir

                query += '''
                    ) as total
                '''

                cur.execute(query, params)
                row = cur.fetchone()

                return bool(row['total'])

    def crear(self, nombre: str) -> CompanySeguros:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    insert into CompanySeguros (nombre, eliminado)
                    values (%(nombre)s, false)
                    returning id, nombre
                '''
                params = {
                    'nombre': nombre
                }

                cur.execute(query, params)
                row = cur.fetchone()
                conn.commit()

                return CompanySeguros(
                    id=row['id'],
                    nombre=row['nombre'],
                )

    def actualizar_nombre(self, id: int, nombre: str) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    update CompanySeguros
                    set nombre = %(nombre)s
                    where id = %(id)s
                '''
                params = {
                    'id': id,
                    'nombre': nombre,
                }

                cur.execute(query, params)
                conn.commit()

    def eliminar(self, id: int) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    update CompanySeguros
                    set eliminado = true
                    where id = %(id)s
                '''
                params = {'id': id}

                cur.execute(query, params)
                conn.commit()

    def reemplazar_factores_cuotas(
        self, id_company: int, factores: list[tuple[int, float]]
    ) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                delete_query = '''
                    delete from FactorCuotasCompany
                    where id_company = %(id_company)s
                '''
                cur.execute(delete_query, {'id_company': id_company})

                insert_query = '''
                    insert into FactorCuotasCompany (id_company, numero_cuotas, factor)
                    values (%(id_company)s, %(numero_cuotas)s, %(factor)s)
                '''

                for numero_cuotas, factor in factores:
                    cur.execute(insert_query, {
                        'id_company': id_company,
                        'numero_cuotas': numero_cuotas,
                        'factor': factor,
                    })

                conn.commit()
