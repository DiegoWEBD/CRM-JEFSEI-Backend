from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.cotizacion.repositorio_cotizaciones import RepositorioCotizaciones
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
                    C.prima_adicional_asistencia,
                    C.id_company,
                    CS.nombre as nombre_company,
                    C.fecha_emision,
                    C.fecha_vencimiento
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
            
    def registrar_cotizacion_a_solicitud(self, id_solicitud: int, cotizacion: Cotizacion):
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    insert into Cotizacion(
                        id_solicitud,
                        id_company, 
                        fecha_emision, 
                        fecha_vencimiento, 
                        monto_total_asegurado, 
                        prima_adicional_asistencia, 
                        tasa_afecta, 
                        tasa_excenta, 
                        tasa_politica
                    )
                    values(
                        %(id_solicitud)s,
                        %(id_company)s, 
                        %(fecha_emision)s, 
                        %(fecha_vencimiento)s, 
                        %(monto_total_asegurado)s, 
                        %(prima_adicional_asistencia)s, 
                        %(tasa_afecta)s, 
                        %(tasa_excenta)s, 
                        %(tasa_politica)s
                    )
                '''

                params = {
                    'id_solicitud': id_solicitud,
                    'id_company': cotizacion.company.id,
                    'fecha_emision': cotizacion.fecha_emision,
                    'fecha_vencimiento': cotizacion.fecha_vencimiento,
                    'monto_total_asegurado': cotizacion.monto_total_asegurado,
                    'prima_adicional_asistencia': cotizacion.prima_adicional_asistencia,
                    'tasa_afecta': cotizacion.tasa_afecta,
                    'tasa_excenta': cotizacion.tasa_excenta,
                    'tasa_politica': cotizacion.tasa_politica
                }

                cur.execute(query, params)