from datetime import datetime

from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.cotizacion.cotizacion import Cotizacion


class CotizacionFactory:

    @staticmethod
    def crear(
        monto_total_asegurado: float,
        prima_adicional_asistencia: float,
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

            prima_afecta = (
                ((monto_total_asegurado * tasa_afecta) / 1000)
                + ((monto_total_asegurado * tasa_politica) / 1000)
                + prima_adicional_asistencia
            )
            prima_excenta = (monto_total_asegurado * tasa_excenta) / 1000
        else:
            prima_afecta = prima_afecta or 0.0
            prima_excenta = prima_excenta or 0.0

            tasa_afecta = (prima_afecta / monto_total_asegurado) * 1000 if monto_total_asegurado else 0.0
            tasa_excenta = (prima_excenta / monto_total_asegurado) * 1000 if monto_total_asegurado else 0.0
            tasa_politica = 0.0

        prima_iva = prima_afecta * 0.19
        prima_neta = prima_afecta + prima_excenta
        prima_bruta = prima_iva + prima_neta

        return Cotizacion(
            id=None,
            monto_total_asegurado=monto_total_asegurado,
            tasa_afecta=tasa_afecta,
            tasa_excenta=tasa_excenta,
            tasa_politica=tasa_politica,
            prima_adicional_asistencia=prima_adicional_asistencia,
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
