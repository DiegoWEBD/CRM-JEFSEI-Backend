from app.dominio.configuracion_condominio.parametros_depreciacion import ParametrosDepreciacion
from app.dominio.configuracion_condominio.repositorio_configuracion_condominio import RepositorioConfiguracionCondominio
from app.dominio.configuracion_condominio.valor_uf_region import ValorUfRegion
from app.infraestructura.configuracion_condominio.adaptadores.dictrow_parametros_depreciacion_adapter import DictRowParametrosDepreciacionAdapter
from app.infraestructura.configuracion_condominio.adaptadores.dictrow_valor_uf_region_adapter import DictRowValorUfRegionAdapter
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioConfiguracionCondominioPostgres(RepositorioConfiguracionCondominio):

    def obtener_valor_uf_por_region(self, region: str) -> float | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    select valor_uf_m2
                    from ValorUfRegion
                    where lower(region) = lower(%(region)s)
                '''
                cur.execute(query, {'region': region})
                row = cur.fetchone()

                if row is None:
                    return None

                return row['valor_uf_m2']

    def obtener_todos_valores_uf_region(self) -> list[ValorUfRegion]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    select id, region, valor_uf_m2
                    from ValorUfRegion
                    order by region
                '''
                cur.execute(query)
                rows = cur.fetchall()

                if not rows:
                    return []

                return [
                    DictRowValorUfRegionAdapter(row).to_valor_uf_region()
                    for row in rows
                ]

    def guardar_valor_uf_region(self, valor: ValorUfRegion) -> ValorUfRegion:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                if valor.id is not None:
                    query = '''
                        update ValorUfRegion
                        set region = %(region)s,
                            valor_uf_m2 = %(valor_uf_m2)s
                        where id = %(id)s
                        returning id
                    '''
                    cur.execute(query, {
                        'id': valor.id,
                        'region': valor.region,
                        'valor_uf_m2': valor.valor_uf_m2,
                    })
                else:
                    query = '''
                        insert into ValorUfRegion (region, valor_uf_m2)
                        values (%(region)s, %(valor_uf_m2)s)
                        on conflict (region) do update
                        set valor_uf_m2 = excluded.valor_uf_m2
                        returning id
                    '''
                    cur.execute(query, {
                        'region': valor.region,
                        'valor_uf_m2': valor.valor_uf_m2,
                    })

                row = cur.fetchone()
                valor.id = row['id'] # type: ignore
                return valor

    def eliminar_valor_uf_region(self, id: int) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    delete from ValorUfRegion
                    where id = %(id)s
                '''
                cur.execute(query, {'id': id})

    def obtener_parametros_depreciacion(self) -> ParametrosDepreciacion | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    select id, antiguedad_sin_depreciacion, porcentaje_por_anio,
                           antiguedad_maxima, porcentaje_maximo
                    from ParametrosDepreciacion
                    limit 1
                '''
                cur.execute(query)
                row = cur.fetchone()

                if row is None:
                    return None

                return DictRowParametrosDepreciacionAdapter(row).to_parametros_depreciacion()

    def guardar_parametros_depreciacion(self, params: ParametrosDepreciacion) -> ParametrosDepreciacion:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                if params.id is not None:
                    query = '''
                        update ParametrosDepreciacion
                        set antiguedad_sin_depreciacion = %(antiguedad_sin_depreciacion)s,
                            porcentaje_por_anio = %(porcentaje_por_anio)s,
                            antiguedad_maxima = %(antiguedad_maxima)s,
                            porcentaje_maximo = %(porcentaje_maximo)s
                        where id = %(id)s
                        returning id
                    '''
                    cur.execute(query, {
                        'id': params.id,
                        'antiguedad_sin_depreciacion': params.antiguedad_sin_depreciacion,
                        'porcentaje_por_anio': params.porcentaje_por_anio,
                        'antiguedad_maxima': params.antiguedad_maxima,
                        'porcentaje_maximo': params.porcentaje_maximo,
                    })
                else:
                    query = '''
                        insert into ParametrosDepreciacion (
                            antiguedad_sin_depreciacion, porcentaje_por_anio,
                            antiguedad_maxima, porcentaje_maximo
                        )
                        values (
                            %(antiguedad_sin_depreciacion)s, %(porcentaje_por_anio)s,
                            %(antiguedad_maxima)s, %(porcentaje_maximo)s
                        )
                        returning id
                    '''
                    cur.execute(query, {
                        'antiguedad_sin_depreciacion': params.antiguedad_sin_depreciacion,
                        'porcentaje_por_anio': params.porcentaje_por_anio,
                        'antiguedad_maxima': params.antiguedad_maxima,
                        'porcentaje_maximo': params.porcentaje_maximo,
                    })

                row = cur.fetchone()
                params.id = row['id'] # type: ignore
                return params
