from datetime import datetime

from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.cotizacion.servicio_calculo_primas import ServicioCalculoPrimas


class CotizacionFactory:

    @staticmethod
    def crear(
        monto_total_asegurado: float,
        asistencia_afecta: float,
        asistencia_excenta: float,
        id_company: int,
        fecha_emision: datetime,
        fecha_vencimiento: datetime,
        tipo: str,
        tasa_afecta: float | None = None,
        tasa_excenta: float | None = None,
        tasa_politica: float | None = None,
        prima_afecta: float | None = None,
        prima_excenta: float | None = None,
        nombre_archivo: str | None = None,
    ) -> Cotizacion:
        company = CompanySeguros(id=id_company, nombre='')

        if tipo == 'tasa':
            tasa_afecta = tasa_afecta or 0.0
            tasa_excenta = tasa_excenta or 0.0
            tasa_politica = tasa_politica or 0.0

            prima_afecta = ServicioCalculoPrimas.calcular_prima_afecta(
                monto_total_asegurado, tasa_afecta, tasa_politica, asistencia_afecta
            )
            prima_excenta = ServicioCalculoPrimas.calcular_prima_excenta(
                monto_total_asegurado, tasa_excenta, asistencia_excenta
            )
        else:
            prima_afecta = (prima_afecta or 0.0) + asistencia_afecta
            prima_excenta = (prima_excenta or 0.0) + asistencia_excenta

            tasa_afecta, tasa_excenta = ServicioCalculoPrimas.calcular_tasas_desde_primas(
                prima_afecta, prima_excenta, monto_total_asegurado
            )
            tasa_politica = 0.0

        prima_iva = ServicioCalculoPrimas.calcular_iva_prima_afecta(prima_afecta)
        prima_neta = ServicioCalculoPrimas.calcular_prima_neta(prima_afecta, prima_excenta)
        prima_bruta = ServicioCalculoPrimas.calcular_prima_bruta(prima_neta, prima_iva)

        return Cotizacion(
            id=None,
            monto_total_asegurado=monto_total_asegurado,
            tasa_afecta=round(tasa_afecta, 2),
            tasa_excenta=round(tasa_excenta, 2),
            tasa_politica=round(tasa_politica, 2),
            asistencia_afecta=asistencia_afecta,
            asistencia_excenta=asistencia_excenta,
            company=company,
            fecha_emision=fecha_emision,
            fecha_vencimiento=fecha_vencimiento,
            nombre_archivo=nombre_archivo,
            prima_afecta=prima_afecta,
            prima_excenta=prima_excenta,
            prima_neta=prima_neta,
            prima_iva=prima_iva,
            prima_bruta=prima_bruta,
        )
