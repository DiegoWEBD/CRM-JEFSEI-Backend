from datetime import datetime, timezone

from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.cotizacion.repositorio_cotizaciones import RepositorioCotizaciones
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.infraestructura.cotizacion.adaptadores.dictrow_cotizacion_adapter import DictRowCotizacionAdapter
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioCotizacionesPostgres(RepositorioCotizaciones):

    def obtener_por_solicitud(self, id_solicitud: int) -> list[Cotizacion]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select C.id,
                    C.monto_total_asegurado,
                    C.tasa_afecta,
                    C.tasa_excenta,
                    C.tasa_politica,
                    C.asistencia_afecta,
                    C.asistencia_excenta,
                    C.prima_afecta,
                    C.prima_excenta,
                    C.prima_neta,
                    C.prima_iva,
                    C.prima_bruta,
                    C.id_company,
                    CS.nombre as nombre_company,
                    C.fecha_emision,
                    C.fecha_vencimiento,
                    C.nombre_archivo
                    from Cotizacion C
                    inner join CompanySeguros CS
                    on C.id_company = CS.id
                    where C.id_solicitud = %(id_solicitud)s
                '''

                params = {
                    'id_solicitud': id_solicitud
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                return [DictRowCotizacionAdapter(row).to_cotizacion() for row in rows]
            
    def obtener_por_id(self, id_cotizacion: int) -> Cotizacion | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    select C.id,
                    C.monto_total_asegurado,
                    C.tasa_afecta,
                    C.tasa_excenta,
                    C.tasa_politica,
                    C.asistencia_afecta,
                    C.asistencia_excenta,
                    C.prima_afecta,
                    C.prima_excenta,
                    C.prima_neta,
                    C.prima_iva,
                    C.prima_bruta,
                    C.id_company,
                    CS.nombre as nombre_company,
                    C.fecha_emision,
                    C.fecha_vencimiento,
                    C.nombre_archivo
                    from Cotizacion C
                    inner join CompanySeguros CS
                    on C.id_company = CS.id
                    where C.id = %(id_cotizacion)s
                '''
                params = {'id_cotizacion': id_cotizacion}
                cur.execute(query, params)
                row = cur.fetchone()

                return DictRowCotizacionAdapter(row).to_cotizacion() if row is not None else None

    def registrar_cotizacion_a_solicitud(self, id_solicitud: int, cotizacion: Cotizacion, rut_usuario: str) -> None:
        ESTADO_COTIZACION_CARGADA = 'COTIZACION_DISPONIBLE'

        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                # Registro de la cotización

                query = '''
                    insert into Cotizacion(
                        id_solicitud,
                        id_company, 
                        fecha_emision, 
                        fecha_vencimiento, 
                        monto_total_asegurado, 
                        asistencia_afecta, 
                        asistencia_excenta, 
                        tasa_afecta, 
                        tasa_excenta, 
                        tasa_politica,
                        prima_afecta,
                        prima_excenta,
                        prima_neta,
                        prima_iva,
                        prima_bruta,
                        nombre_archivo
                    )
                    values(
                        %(id_solicitud)s,
                        %(id_company)s, 
                        %(fecha_emision)s, 
                        %(fecha_vencimiento)s, 
                        %(monto_total_asegurado)s, 
                        %(asistencia_afecta)s, 
                        %(asistencia_excenta)s, 
                        %(tasa_afecta)s, 
                        %(tasa_excenta)s, 
                        %(tasa_politica)s,
                        %(prima_afecta)s,
                        %(prima_excenta)s,
                        %(prima_neta)s,
                        %(prima_iva)s,
                        %(prima_bruta)s,
                        %(nombre_archivo)s
                    )
                '''

                params = {
                    'id_solicitud': id_solicitud,
                    'id_company': cotizacion.company.id,
                    'fecha_emision': cotizacion.fecha_emision,
                    'fecha_vencimiento': cotizacion.fecha_vencimiento,
                    'monto_total_asegurado': cotizacion.monto_total_asegurado,
                    'asistencia_afecta': cotizacion.asistencia_afecta,
                    'asistencia_excenta': cotizacion.asistencia_excenta,
                    'tasa_afecta': cotizacion.tasa_afecta,
                    'tasa_excenta': cotizacion.tasa_excenta,
                    'tasa_politica': cotizacion.tasa_politica,
                    'prima_afecta': cotizacion.prima_afecta,
                    'prima_excenta': cotizacion.prima_excenta,
                    'prima_neta': cotizacion.prima_neta,
                    'prima_iva': cotizacion.prima_iva,
                    'prima_bruta': cotizacion.prima_bruta,
                    'nombre_archivo': cotizacion.nombre_archivo
                }

                cur.execute(query, params)

                # Registro del estado

                query = '''
                    select PC.id as id_proceso_comercial
                    from SolicitudCotizacion SC
                    inner join ProcesoComercial PC
                    on SC.id_proceso_comercial = PC.id
                    where SC.id = %(id_solicitud)s
                '''

                params = {
                    'id_solicitud': id_solicitud
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    return

                id_proceso_comercial: int = row['id_proceso_comercial']

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
                    'id_proceso_comercial': id_proceso_comercial,
                    'codigo_estado': ESTADO_COTIZACION_CARGADA,
                    'rut_registrado_por': rut_usuario
                }

                cur.execute(query, params)

                query = '''
                    update ProcesoComercial
                    set codigo_estado_actual = %(codigo_estado)s
                    where id = %(id_proceso_comercial)s
                '''

                params = {
                    'id_proceso_comercial': id_proceso_comercial,
                    'codigo_estado': ESTADO_COTIZACION_CARGADA
                }

                cur.execute(query, params)

    def registrar_renovacion_cotizada(self, numero_poliza_renovacion: str):
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                # Registro de la cotización

                query = '''
                    update Poliza
                    set renovacion_cotizada = true
                    where numero_poliza = %(numero_poliza)s
                '''

                params = {
                    'numero_poliza': numero_poliza_renovacion
                }

                cur.execute(query, params)

    def eliminar(self, cotizacion: Cotizacion) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    delete from Cotizacion
                    where id = %(id)s
                '''

                params = {
                    'id': cotizacion.id
                }

                cur.execute(query, params)

    def actualizar(self, id_cotizacion: int, cotizacion: Cotizacion) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    update Cotizacion set
                        id_company = %(id_company)s,
                        fecha_emision = %(fecha_emision)s,
                        fecha_vencimiento = %(fecha_vencimiento)s,
                        monto_total_asegurado = %(monto_total_asegurado)s,
                        asistencia_afecta = %(asistencia_afecta)s,
                        asistencia_excenta = %(asistencia_excenta)s,
                        tasa_afecta = %(tasa_afecta)s,
                        tasa_excenta = %(tasa_excenta)s,
                        tasa_politica = %(tasa_politica)s,
                        prima_afecta = %(prima_afecta)s,
                        prima_excenta = %(prima_excenta)s,
                        prima_neta = %(prima_neta)s,
                        prima_iva = %(prima_iva)s,
                        prima_bruta = %(prima_bruta)s,
                        nombre_archivo = %(nombre_archivo)s
                    where id = %(id)s
                '''

                params = {
                    'id': id_cotizacion,
                    'id_company': cotizacion.company.id,
                    'fecha_emision': cotizacion.fecha_emision,
                    'fecha_vencimiento': cotizacion.fecha_vencimiento,
                    'monto_total_asegurado': cotizacion.monto_total_asegurado,
                    'asistencia_afecta': cotizacion.asistencia_afecta,
                    'asistencia_excenta': cotizacion.asistencia_excenta,
                    'tasa_afecta': cotizacion.tasa_afecta,
                    'tasa_excenta': cotizacion.tasa_excenta,
                    'tasa_politica': cotizacion.tasa_politica,
                    'prima_afecta': cotizacion.prima_afecta,
                    'prima_excenta': cotizacion.prima_excenta,
                    'prima_neta': cotizacion.prima_neta,
                    'prima_iva': cotizacion.prima_iva,
                    'prima_bruta': cotizacion.prima_bruta,
                    'nombre_archivo': cotizacion.nombre_archivo,
                }

                cur.execute(query, params)

    def cotizacion_pertenece_a_solicitud(self, cotizacion: Cotizacion, id_solicitud: int) -> bool:
        with obtener_conexion() as conn:
                with conn.cursor() as cur:
                    query = '''
                        select id_solicitud
                        from Cotizacion
                        where id = %(id_cotizacion)s
                    '''
    
                    params = {
                        'id_cotizacion': cotizacion.id
                    }
    
                    cur.execute(query, params)
                    row = cur.fetchone()

                    if row is None:
                        return False

                    return row['id_solicitud'] == id_solicitud