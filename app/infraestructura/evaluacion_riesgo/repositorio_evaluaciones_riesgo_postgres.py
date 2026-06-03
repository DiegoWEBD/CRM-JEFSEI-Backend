from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo
from app.dominio.evaluacion_riesgo.repositorio_evaluaciones_riesgo import RepositorioEvaluacionesRiesgo
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.evaluacion_riesgo.adaptadores.dictrows_evaluacion_riesgo_adapter import DictRowsEvaluacionRiesgoAdapter


class RepositorioEvaluacionesRiesgoPostgres(RepositorioEvaluacionesRiesgo):

    def buscar_evaluacion(self, id_prospecto: int) -> EvaluacionRiesgo | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select ER.id, ER.uf_por_metro_cuadrado,
                    ER.porcentaje_depreciacion, ER.porcentaje_espacios_comunes,
                    ER.observaciones, C.id as id_cotizacion,
                    C.monto_total_asegurado as cotizacion_monto_total_asegurado,
                    C.tasa_afecta as cotizacion_tasa_afecta,
                    C.tasa_excenta as cotizacion_tasa_excenta,
                    C.tasa_politica as cotizacion_tasa_politica,
                    C.prima_adicional_asistencia as cotizacion_prima_adicional_asistencia,
                    C.fecha_emision as cotizacion_fecha_emision, 
                    C.fecha_vencimiento as cotizacion_fecha_vencimiento,
                    C.id_company, CS.nombre as nombre_company,
                    ECC.id as id_estudio_comercial,
                    ECC.cantidad_cuotas, ECC.valor_uf,
                    DECC.porcentaje_infraseguro,
                    DECC.iva_prima_afecta,
                    DECC.prima_neta as detalle_prima_neta,
                    DECC.prima_bruta as detalle_prima_bruta
                    from EvaluacionRiesgo ER
                    inner join SolicitudEvaluacionRiesgo SER
                    on ER.id_solicitud = SER.id
                    inner join ProcesoComercial PC
                    on SER.id_proceso_comercial = PC.id
                    inner join Prospecto P
                    on PC.id_prospecto = P.id
                    left join Cotizacion C
                    on ER.id = C.id_evaluacion
                    inner join CompanySeguros CS
                    on C.id_company = CS.id
                    left join DetalleEstudioComercialCondominio DECC
                    on C.id = DECC.id_cotizacion
                    left join EstudioComercialCondominio ECC
                    on DECC.id_estudio_comercial = ECC.id
                    where P.id = %(id)s
                '''

                params = {
                    'id': id_prospecto
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                if rows is None or len(rows) == 0:
                    return None
                
                return DictRowsEvaluacionRiesgoAdapter(rows).to_evaluacion_riesgo()