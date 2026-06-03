from psycopg.rows import DictRow

from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.estudio_comercial.detalle_estudio_comercial.detalle_estudio_comercial import DetalleEstudioComercial
from app.dominio.estudio_comercial.estudio_comercial_condominio.estudio_comercial_condominio import EstudioComercialCondominio
from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo


class DictRowsEvaluacionRiesgoAdapter:

    def __init__(self, rows: list[DictRow]) -> None:
        if rows is None or len(rows) == 0:
            raise Exception('Evaluación de riesgo inválida')

        self.rows = rows

    def to_evaluacion_riesgo(self) -> EvaluacionRiesgo:
        
        id = self.rows[0]['id']
        uf_por_metro_cuadrado = self.rows[0]['uf_por_metro_cuadrado']
        porcentaje_depreciacion = self.rows[0]['porcentaje_depreciacion']
        porcentaje_espacios_comunes = self.rows[0]['porcentaje_espacios_comunes']
        observaciones = self.rows[0]['observaciones']

        evaluacion = EvaluacionRiesgo(
            id=id,
            uf_por_metro_cuadrado=uf_por_metro_cuadrado,
            porcentaje_depreciacion=porcentaje_depreciacion,
            porcentaje_espacios_comunes=porcentaje_espacios_comunes,
            observaciones=observaciones
        )

        id_estudio_comercial = self.rows[0]['id_estudio_comercial']
        cantidad_cuotas = self.rows[0]['cantidad_cuotas']
        valor_uf = self.rows[0]['valor_uf']

        detalles_estudio: list[DetalleEstudioComercial] = []
        cotizaciones: list[Cotizacion] = []

        for row in self.rows:
            id_cotizacion = row['id_cotizacion']

            if id_cotizacion is None:
                break

            cotizacion_monto_total_asegurado = row['cotizacion_monto_total_asegurado']
            cotizacion_tasa_afecta = row['cotizacion_tasa_afecta']
            cotizacion_tasa_excenta = row['cotizacion_tasa_excenta']
            cotizacion_tasa_politica = row['cotizacion_tasa_politica']
            cotizacion_prima_adicional_asistencia = row['cotizacion_prima_adicional_asistencia']
            cotizacion_fecha_emision = row['cotizacion_fecha_emision']
            cotizacion_fecha_vencimiento = row['cotizacion_fecha_vencimiento']
            id_company = row['id_company']
            nombre_company = row['nombre_company']

            company = CompanySeguros(
                id=id_company,
                nombre=nombre_company
            )

            cotizacion = Cotizacion(
                id=id_cotizacion,
                monto_total_asegurado=cotizacion_monto_total_asegurado,
                tasa_afecta=cotizacion_tasa_afecta,
                tasa_excenta=cotizacion_tasa_excenta,
                tasa_politica=cotizacion_tasa_politica,
                prima_adicional_asistencia=cotizacion_prima_adicional_asistencia,
                company=company,
                fecha_emision=cotizacion_fecha_emision,
                fecha_vencimiento=cotizacion_fecha_vencimiento
            )

            cotizaciones.append(cotizacion)

            if id_estudio_comercial is not None:
                porcentaje_infraseguro = row['porcentaje_infraseguro']
                iva_prima_afecta = row['iva_prima_afecta']
                detalle_prima_neta = row['detalle_prima_neta']
                detalle_prima_bruta = row['detalle_prima_bruta']

                detalle = DetalleEstudioComercial(
                    cotizacion=cotizacion,
                    porcentaje_infraseguro=porcentaje_infraseguro,
                    iva_prima_afecta=iva_prima_afecta,
                    prima_neta=detalle_prima_neta,
                    prima_bruta=detalle_prima_bruta
                )

                detalles_estudio.append(detalle)

        evaluacion.cotizaciones = cotizaciones

        if id_estudio_comercial is not None:
            estudio = EstudioComercialCondominio(
                cantidad_cuotas=cantidad_cuotas,
                valor_uf=valor_uf,
                detalles=detalles_estudio
            )
            evaluacion.estudio = estudio

        return evaluacion