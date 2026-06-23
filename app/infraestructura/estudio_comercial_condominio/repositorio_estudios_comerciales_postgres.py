from app.aplicacion.evaluacion_proyectos.dto.estudio_comercial_condominio_resumen import EstudioComercialCondominioResumen
from app.dominio.estudio_comercial.estudio_comercial_condominio.estudio_comercial_condominio import EstudioComercialCondominio
from app.dominio.estudio_comercial.estudio_comercial_condominio.repositorio_estudios_comerciales import RepositorioEstudiosComerciales
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioEstudiosComercialesPostgres(RepositorioEstudiosComerciales):
    ESTADO_ESTUDIO_DISPONIBLE = 'ESTUDIO_DISPONIBLE'

    def registrar(
        self,
        estudio: EstudioComercialCondominio,
        ids_cotizacion: list[int],
        rut_usuario: str
    ) -> int:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    insert into EstudioComercialCondominio (cantidad_cuotas, valor_uf)
                    values (%(cantidad_cuotas)s, %(valor_uf)s)
                    returning id
                '''

                params = {
                    'cantidad_cuotas': estudio.cantidad_cuotas,
                    'valor_uf': estudio.valor_uf
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    raise Exception('Error al registrar el estudio comercial')

                id_estudio: int = row['id']

                detalles_por_grupo = [
                    *estudio.detalles_monto_asegurado_actual,
                    *estudio.detalles_monto_asegurado_sugerido,
                    *estudio.detalles_monto_asegurado_primer_ejemplo,
                    *estudio.detalles_monto_asegurado_segundo_ejemplo,
                ]

                for detalle in detalles_por_grupo:
                    query = '''
                        insert into DetalleEstudioComercialCondominio (
                            id_estudio_comercial,
                            id_cotizacion,
                            porcentaje_infraseguro,
                            iva_prima_afecta,
                            prima_neta,
                            prima_bruta
                        )
                        values (
                            %(id_estudio_comercial)s,
                            %(id_cotizacion)s,
                            %(porcentaje_infraseguro)s,
                            %(iva_prima_afecta)s,
                            %(prima_neta)s,
                            %(prima_bruta)s
                        )
                    '''

                    params = {
                        'id_estudio_comercial': id_estudio,
                        'id_cotizacion': detalle.cotizacion.id,
                        'porcentaje_infraseguro': detalle.porcentaje_infraseguro,
                        'iva_prima_afecta': detalle.iva_prima_afecta,
                        'prima_neta': detalle.prima_neta,
                        'prima_bruta': detalle.prima_bruta,
                    }

                    cur.execute(query, params)

                query = '''
                    select PC.id as id_proceso_comercial
                    from Cotizacion C
                    inner join SolicitudCotizacion SC on C.id_solicitud = SC.id
                    inner join ProcesoComercial PC on SC.id_proceso_comercial = PC.id
                    where C.id = any(%(ids_cotizacion)s)
                    limit 1
                '''

                params = {
                    'ids_cotizacion': ids_cotizacion
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is not None:
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
                        'codigo_estado': self.ESTADO_ESTUDIO_DISPONIBLE,
                        'rut_registrado_por': rut_usuario,
                    }

                    cur.execute(query, params)

                    query = '''
                        update ProcesoComercial
                        set codigo_estado_actual = %(codigo_estado)s
                        where id = %(id_proceso_comercial)s
                    '''

                    params = {
                        'id_proceso_comercial': id_proceso_comercial,
                        'codigo_estado': self.ESTADO_ESTUDIO_DISPONIBLE,
                    }

                    cur.execute(query, params)

                return id_estudio

    def actualizar_ruta_archivo(
        self,
        id_estudio: int,
        ruta_archivo: str
    ) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    update EstudioComercialCondominio
                    set ruta_archivo = %(ruta_archivo)s,
                        fecha_emision = current_date
                    where id = %(id_estudio)s
                '''

                params = {
                    'id_estudio': id_estudio,
                    'ruta_archivo': ruta_archivo
                }

                cur.execute(query, params)

    def listar_por_id_solicitud_cotizacion(
        self,
        id_solicitud: int
    ) -> list[EstudioComercialCondominioResumen]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select ECC.id as id_estudio_comercial,
                    DECC.id as id_detalle,
                    ECC.cantidad_cuotas, 
                    ECC.valor_uf,
                    DECC.porcentaje_infraseguro,
                    DECC.iva_prima_afecta,
                    DECC.prima_neta,
                    DECC.prima_bruta,
                    CS.nombre as company
                    from SolicitudCotizacion SC
                    inner join Cotizacion C
                    on SC.id = C.id_solicitud
                    inner join CompanySeguros CS
                    on C.id_company = CS.id
                    inner join DetalleEstudioComercialCondominio DECC
                    on C.id = DECC.id_cotizacion
                    inner join EstudioComercialCondominio ECC
                    on DECC.id_estudio_comercial = ECC.id
                    where SC.id = %(id_solicitud)s
                    order by id desc
                '''

                params = {
                    'id_solicitud': id_solicitud
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                return [
                    EstudioComercialCondominioResumen(
                        id=row['id'],
                        cantidad_cuotas=row['cantidad_cuotas'],
                        valor_uf=row['valor_uf'],
                        ruta_archivo=None,
                        fecha_emision=None
                    )
                    for row in rows
                ]
