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