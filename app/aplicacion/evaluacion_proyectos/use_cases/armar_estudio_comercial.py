from app.dominio.estudio_comercial.estudio_comercial import EstudioComercial


class ArmarEstudioComercialUseCase:

    def ejecutar(
        self,
        monto_asegurado_actual: float,
        infraseguro_primer_ejemplo: float,
        infraseguro_segundo_ejemplo: float,
        metros_cuadrados_construidos: float,
        valor_uf_por_metro_cuadrado: float,
        porcentaje_depreciacion: float,
        cantidad_cuotas: int,
        porcentaje_bienes_espacios_comunes: float,

    ) -> EstudioComercial:
        
        factor_iva = 1.19
        valor_total_reconstruccion_iva = round(metros_cuadrados_construidos * valor_uf_por_metro_cuadrado * factor_iva)
        valor_total_reconstruccion_depreciacion_iva = round((1 - porcentaje_depreciacion) * valor_total_reconstruccion_iva)
        monto_asegurado_sugerido = round(valor_total_reconstruccion_depreciacion_iva * porcentaje_bienes_espacios_comunes)
        infraseguro_actual = round(1 - (monto_asegurado_actual / monto_asegurado_sugerido), 2)
        monto_asegurado_primer_ejemplo = round(monto_asegurado_sugerido * (1 - infraseguro_primer_ejemplo))
        monto_asegurado_segundo_ejemplo = round(monto_asegurado_sugerido * (1 - infraseguro_segundo_ejemplo))

        estudio = EstudioComercial(
            monto_asegurado_actual=monto_asegurado_actual,
            infraseguro_primer_ejemplo=infraseguro_primer_ejemplo,
            infraseguro_segundo_ejemplo=infraseguro_segundo_ejemplo,
            metros_cuadrados_construidos=metros_cuadrados_construidos,
            valor_uf_por_metro_cuadrado=valor_uf_por_metro_cuadrado,
            porcentaje_depreciacion=porcentaje_depreciacion,
            cantidad_cuotas=cantidad_cuotas,
            porcentaje_bienes_espacios_comunes=porcentaje_bienes_espacios_comunes,
            valor_total_reconstruccion_iva=valor_total_reconstruccion_iva,
            valor_total_reconstruccion_depreciacion_iva=valor_total_reconstruccion_depreciacion_iva,
            monto_asegurado_sugerido=monto_asegurado_sugerido,
            infraseguro_actual=infraseguro_actual,
            monto_asegurado_primer_ejemplo=monto_asegurado_primer_ejemplo,
            monto_asegurado_segundo_ejemplo=monto_asegurado_segundo_ejemplo
        )

        return estudio
    
    def __detalle_estudio_condominio_segun_primas(monto_total_asegurado: float, prima_afecta: float, prima_excenta: float):

        factor_iva = 0.19
        iva_prima_afecta = prima_afecta * factor_iva
        prima_neta = prima_afecta + prima_excenta
        prima_bruta = iva_prima_afecta + prima_neta
        tasa_afecta = (prima_afecta / monto_total_asegurado) * 1000
        tasa_excenta = (prima_excenta / monto_total_asegurado) * 1000
        tasa_total = tasa_afecta + tasa_excenta