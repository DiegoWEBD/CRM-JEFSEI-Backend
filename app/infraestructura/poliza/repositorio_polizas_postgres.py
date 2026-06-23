from dateutil.relativedelta import relativedelta
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.poliza.poliza import Poliza
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.poliza.adapadores.dictrow_poliza_adapter import DictRowPolizaAdapter


class RepositorioPolizasPostgres(RepositorioPolizas):

    def buscar(self, numero_poliza: str) -> Poliza | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                
                query = '''
                    select P.numero_poliza, 
                    P.tipo, P.prima_neta, 
                    P.comision_corredora_pct,
                    CS.nombre as company,
                    PR.nombre as nombre_producto,
                    P.fecha_emision,
                    P.inicio_vigencia,
                    P.fin_vigencia,
                    P.id_company,
                    P.cancelada,
                    P.renovacion_cotizada
                    from Poliza P
                    inner join ProcesoComercial PC
                    on P.id_proceso_comercial = PC.id
                    inner join Producto PR
                    on PC.id_producto = PR.id
                    left join CompanySeguros CS
                    on P.id_company = CS.id
                    where P.numero_poliza = %(numero_poliza)s
                '''

                params = {
                    'numero_poliza': numero_poliza
                }

                cur.execute(query, params)
                row = cur.fetchone()

                return DictRowPolizaAdapter(row).to_poliza() if row else None

    def obtener_polizas_cliente(self, id_cliente: int, rut_usuario: str | None) -> list[Poliza]:
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
                    P.tipo, P.prima_neta, 
                    P.comision_corredora_pct,
                    CS.nombre as company,
                    PR.nombre as nombre_producto,
                    P.fecha_emision,
                    P.inicio_vigencia,
                    P.fin_vigencia,
                    P.id_company,
                    P.cancelada,
                    P.renovacion_cotizada
                    from Poliza P
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
                    P.tipo, P.prima_neta, 
                    P.comision_corredora_pct,
                    CS.id as id_company,
                    CS.nombre as company,
                    PR.nombre as nombre_producto,
                    P.fecha_emision,
                    P.inicio_vigencia,
                    P.fin_vigencia,
                    P.id_company,
                    P.cancelada,
                    P.renovacion_cotizada
                    from Poliza P
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

    def registrar_a_proceso_comercial(self, poliza: Poliza, id_proceso_comercial: int) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select C.id as id_cliente,
                    P.id as id_prospecto
                    from ProcesoComercial PC
                    inner join Prospecto P
                    on PC.id_prospecto = P.id
                    left join Cliente C
                    on P.id = C.id_prospecto
                    where PC.id = %(id_proceso_comercial)s
                '''

                params = {
                    'id_proceso_comercial': id_proceso_comercial
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    return
                
                id_prospecto = row['id_prospecto']
                id_cliente = row['id_cliente']

                if not id_cliente:
                    # Crear cliente en caso que no lo sea

                    query = '''
                        insert into Cliente (id_prospecto)
                        values (%(id_prospecto)s)
                        returning id
                    '''

                    params = {
                        'id_prospecto': id_prospecto
                    }

                    cur.execute(query, params)
                    row = cur.fetchone()

                    if not row:
                        return
                    
                    id_cliente = row['id']

                # Registrar póliza
                query = '''
                    insert into Poliza (
                        numero_poliza,
                        id_cliente,
                        tipo,
                        prima_neta,
                        comision_corredora_pct,
                        fecha_emision,
                        inicio_vigencia,
                        fin_vigencia,
                        id_company,
                        id_proceso_comercial,
                        cancelada,
                        renovacion_cotizada
                    )
                    values (
                        %(numero_poliza)s,
                        %(id_cliente)s,
                        %(tipo)s,
                        %(prima_neta)s,
                        %(comision_corredora_pct)s,
                        %(fecha_emision)s,
                        %(inicio_vigencia)s,
                        %(fin_vigencia)s,
                        %(id_company)s,
                        %(id_proceso_comercial)s,
                        %(cancelada)s,
                        %(renovacion_cotizada)s
                    )
                '''

                params = {
                    'numero_poliza': poliza.numero_poliza,
                    'id_cliente': id_cliente,
                    'tipo': poliza.tipo,
                    'prima_neta': poliza.prima_neta,
                    'comision_corredora_pct': poliza.comision_corredora_pct,
                    'fecha_emision': poliza.fecha_emision,
                    'inicio_vigencia': poliza.inicio_vigencia,
                    'fin_vigencia': poliza.fin_vigencia,
                    'id_company': poliza.company.id if poliza.company else None,
                    'id_proceso_comercial': id_proceso_comercial,
                    'cancelada': False,
                    'renovacion_cotizada': False
                }

                cur.execute(query, params)

                if not poliza.fin_vigencia:
                    return
                
                fecha_recordatorio_cotizacion = poliza.fin_vigencia - relativedelta(months=2)
                fecha_recordatorio_contacto = poliza.fin_vigencia - relativedelta(days=20)

                # Registrar recordatorio para comenzar a cotizar renovación

                query = '''
                    insert into RecordatorioPostVentaPoliza (
                        numero_poliza,
                        titulo,
                        detalle,
                        completado,
                        tipo_gestion,
                        fecha_recordatorio
                    )
                    values (
                        %(numero_poliza)s,
                        %(titulo)s,
                        %(detalle)s,
                        %(completado)s,
                        %(tipo_gestion)s,
                        %(fecha_recordatorio)s
                    )
                '''

                params = {
                    'numero_poliza': poliza.numero_poliza,
                    'titulo': 'Iniciar cotización para renovación',
                    'detalle': f'El día {poliza.fin_vigencia.strftime("%d-%m-%Y")} vence la póliza {poliza.numero_poliza} ({poliza.nombre_producto}), por lo que debe comenzar a cotizar para su renovación',
                    'completado': False,
                    'tipo_gestion': 'renovacion_cotizacion',
                    'fecha_recordatorio': fecha_recordatorio_cotizacion
                }

                cur.execute(query, params)

                # Registrar recordatorio para comenzar la gestión de la renovación

                query = '''
                    insert into RecordatorioPostVentaPoliza (
                        numero_poliza,
                        titulo,
                        detalle,
                        completado,
                        tipo_gestion,
                        fecha_recordatorio
                    )
                    values (
                        %(numero_poliza)s,
                        %(titulo)s,
                        %(detalle)s,
                        %(completado)s,
                        %(tipo_gestion)s,
                        %(fecha_recordatorio)s
                    )
                '''

                params = {
                    'numero_poliza': poliza.numero_poliza,
                    'titulo': 'Iniciar cotización para renovación',
                    'detalle': f'El día {poliza.fin_vigencia.strftime("%d-%m-%Y")} vence la póliza {poliza.numero_poliza} ({poliza.nombre_producto}), por lo que debe comenzar a gestionar su renovación',
                    'completado': False,
                    'tipo_gestion': 'renovacion_cotizacion',
                    'fecha_recordatorio': fecha_recordatorio_contacto
                }

                cur.execute(query, params)