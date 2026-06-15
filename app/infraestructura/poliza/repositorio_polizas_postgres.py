from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.poliza.poliza import Poliza
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.poliza.adapadores.dictrow_poliza_adapter import DictRowPolizaAdapter


class RepositorioPolizasPostgres(RepositorioPolizas):

    def buscar(self, id_cliente: int, rut_usuario: str | None) -> list[Poliza]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                
                query = '''
                    select id
                    from Cliente
                    where id = %(id_cliente)s
                '''

                params = {
                    'id_cliente': id_cliente
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    raise RecursoNoEncontradoException('Cliente no encontrado')

                if rut_usuario is not None:
                    autorizado = False

                    query = '''
                        select P.rut_registrado_por,
                        P.rut_ej_comercial_asignado,
                        PC.rut_ej_comercial as rut_ej_comercial_proceso,
                        PC.rut_ej_evaluacion
                        from Cliente C
                        inner join Prospecto P
                        on C.id_prospecto = P.id
                        inner join ProcesoComercial PC
                        on P.id = PC.id_prospecto
                        where C.id = %(id_cliente)s
                    '''

                    params = {
                        'id_cliente': id_cliente
                    }

                    cur.execute(query, params)
                    rows = cur.fetchall()

                    for row in rows:
                        rut_registrado_por = row['rut_registrado_por']
                        rut_ej_comercial_asignado = row['rut_ej_comercial_asignado']
                        rut_ej_comercial_proceso = row['rut_ej_comercial_proceso']
                        rut_ej_evaluacion = row['rut_ej_evaluacion']

                        if rut_usuario == rut_registrado_por or rut_usuario == rut_ej_comercial_asignado or rut_usuario == rut_ej_comercial_proceso or rut_usuario == rut_ej_evaluacion:
                            autorizado = True
                            break

                    if not autorizado:
                        raise UsuarioNoAutorizadoException        

                query = '''
                    select P.numero_poliza, 
                    P.id_cliente, TP.tipo,
                    P.prima_neta, P.comision_corredora_pct,
                    CS.nombre as company,
                    PR.nombre as nombre_producto,
                    P.fecha_emision,
                    P.inicio_vigencia,
                    P.fin_vigencia,
                    P.id_company,
                    P.cancelada
                    from Poliza P
                    inner join TipoPoliza TP
                    on P.id_tipo_poliza = TP.id
                    inner join ProcesoComercial PC
                    on P.id_proceso_comercial = PC.id
                    inner join Producto PR
                    on PC.id_producto = PR.id
                    left join CompanySeguros CS
                    on P.id_company = CS.id
                    where P.id_cliente = %(id_cliente)s
                '''

                params = {
                    'id_cliente': id_cliente
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                return [DictRowPolizaAdapter(row).to_poliza() for row in rows]
    
    def polizas_gestionadas_ej_comercial_mes_actual(self, rut_ejecutivo: str) -> list[Poliza]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select P.numero_poliza, 
                    TP.tipo, P.prima_neta, 
                    P.comision_corredora_pct,
                    CS.nombre as company,
                    PR.nombre as nombre_producto,
                    P.fecha_emision,
                    P.inicio_vigencia,
                    P.fin_vigencia,
                    P.id_company,
                    P.cancelada
                    from Poliza P
                    inner join TipoPoliza TP
                    on P.id_tipo_poliza = TP.id
                    inner join ProcesoComercial PC
                    on P.id_proceso_comercial = PC.id
                    inner join Producto PR
                    on PC.id_producto = PR.id
                    left join CompanySeguros CS
                    on P.id_company = CS.id
                    where extract(year from P.fecha_emision) = extract(year from current_date)
                    and extract(month from P.fecha_emision) = extract(month from current_date)
                    and PC.rut_ej_comercial = %(rut_ejecutivo)s
                '''

                params = {
                    'rut_ejecutivo': rut_ejecutivo
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                return [DictRowPolizaAdapter(row).to_poliza() for row in rows]

    def registrar(self, poliza: Poliza) -> None:
        pass