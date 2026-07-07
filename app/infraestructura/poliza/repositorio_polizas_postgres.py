from dateutil.relativedelta import relativedelta
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.plan_pago.plan_pago import PlanPago
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
                    P.id_proceso_comercial,
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
            
    def buscar_por_proceso_comercial(self, id_proceso_comercial: int) -> Poliza | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                
                query = '''
                    select P.numero_poliza, 
                    P.tipo, P.prima_neta, 
                    P.id_proceso_comercial,
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
                    where PC.id = %(id_proceso_comercial)s
                '''

                params = {
                    'id_proceso_comercial': id_proceso_comercial
                }

                cur.execute(query, params)
                row = cur.fetchone()

                return DictRowPolizaAdapter(row).to_poliza() if row else None

    def obtener_polizas_cliente(self, id_cliente: int) -> list[Poliza]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:   

                query = '''
                    select P.numero_poliza, 
                    P.tipo, P.prima_neta, 
                    P.id_proceso_comercial,
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
                    P.id_proceso_comercial,
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

    def registrar_a_proceso_comercial(self, poliza: Poliza, id_proceso_comercial: int, rut_usuario: str) -> None:
        ESTADO_POLIZA_REGISTRADA = 'POLIZA_REGISTRADA'

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
                    insert into Recordatorio (
                        titulo,
                        detalle,
                        prioridad,
                        completado,
                        tipo_gestion,
                        fecha_recordatorio
                    )
                    values (
                        %(titulo)s,
                        %(detalle)s,
                        %(prioridad)s,
                        %(completado)s,
                        %(tipo_gestion)s,
                        %(fecha_recordatorio)s
                    )
                    returning id
                '''

                params = {
                    'titulo': 'Iniciar cotización para renovación',
                    'detalle': f'El día {poliza.fin_vigencia.strftime("%d-%m-%Y")} vence la póliza {poliza.numero_poliza}, por lo que debe comenzar a cotizar para su renovación',
                    'prioridad': 'alta',
                    'completado': False,
                    'tipo_gestion': 'renovacion_cotizacion',
                    'fecha_recordatorio': fecha_recordatorio_cotizacion
                }

                cur.execute(query, params)
                row = cur.fetchone()
                id_recordatorio = row['id'] # type: ignore

                query = '''
                    insert into RecordatorioRenovacionPoliza (
                        id,
                        numero_poliza
                    )
                    values (
                        %(id)s,
                        %(numero_poliza)s
                    )
                '''

                params = {
                    'id': id_recordatorio,
                    'numero_poliza': poliza.numero_poliza
                }

                cur.execute(query, params)

                # Registrar recordatorio para comenzar la gestión de la renovación

                query = '''
                    insert into Recordatorio (
                        titulo,
                        detalle,
                        prioridad,
                        completado,
                        tipo_gestion,
                        fecha_recordatorio
                    )
                    values (
                        %(titulo)s,
                        %(detalle)s,
                        %(prioridad)s,
                        %(completado)s,
                        %(tipo_gestion)s,
                        %(fecha_recordatorio)s
                    )
                    returning id
                '''

                params = {
                    'titulo': 'Gestionar renovación',
                    'detalle': f'El día {poliza.fin_vigencia.strftime("%d-%m-%Y")} vence la póliza {poliza.numero_poliza}, por lo que debe gestionar su renovación',
                    'prioridad': 'alta',
                    'completado': False,
                    'tipo_gestion': 'renovacion',
                    'fecha_recordatorio': fecha_recordatorio_contacto
                }

                cur.execute(query, params)
                row = cur.fetchone()
                id_recordatorio = row['id'] # type: ignore

                query = '''
                    insert into RecordatorioRenovacionPoliza (
                        id,
                        numero_poliza
                    )
                    values (
                        %(id)s,
                        %(numero_poliza)s
                    )
                '''

                params = {
                    'id': id_recordatorio,
                    'numero_poliza': poliza.numero_poliza
                }

                cur.execute(query, params)

                # Registro de historial

                query = '''
                    insert into HistorialEstadoInformativoProcesoComercial (
                        id_proceso_comercial,
                        codigo_estado,
                        rut_registrado_por
                    )
                    select
                        %(id_proceso_comercial)s,
                        %(codigo_estado)s,
                        %(rut_registrado_por)s
                    where coalesce(
                        (
                            select codigo_estado
                            from HistorialEstadoInformativoProcesoComercial
                            where id_proceso_comercial = %(id_proceso_comercial)s
                            order by fecha_registro desc
                            limit 1
                        ),
                        ''
                    ) <> %(codigo_estado)s
                '''

                params = {
                    'id_proceso_comercial': poliza.id_proceso_comercial,
                    'codigo_estado': ESTADO_POLIZA_REGISTRADA,
                    'rut_registrado_por': rut_usuario
                }

                cur.execute(query, params)

    def actualizar_cancelada(self, numero_poliza: str, cancelada: bool) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    update Poliza
                    set cancelada = %(cancelada)s
                    where numero_poliza = %(numero_poliza)s
                '''

                params = {
                    'numero_poliza': numero_poliza,
                    'cancelada': cancelada
                }

                cur.execute(query, params)
