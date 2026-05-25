from app.dominio.company_seguros.repositorio_company_seguros import RepositorioCompanySeguros
from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.estudio_comercial.detalle_estudio_comercial.detalle_estudio_comercial import DetalleEstudioComercial
from app.dominio.estudio_comercial.estudio_comercial_condominio.estudio_comercial_condominio import EstudioComercialCondominio
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos


class ArmarEstudioComercialCondominioUseCase:
    factor_iva: float = 0.19

    def __init__(
        self,
        repositorio_prospectos: RepositorioProspectos,
        repositorio_company_seguros: RepositorioCompanySeguros
    ):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_company_seguros = repositorio_company_seguros

    def ejecutar(
        self,
        id_prospecto: int,
        infraseguro_primer_ejemplo: float,
        infraseguro_segundo_ejemplo: float,
        cantidad_cuotas: int
    ) -> EstudioComercialCondominio:

        prospecto = self.repositorio_prospectos.buscar_prospecto_condominio(id_prospecto)

        if not prospecto:
            raise ValueError('Prospecto no encontrado')
        
        monto_asegurado_actual = prospecto.planificacion_prospecto.monto_asegurado_vigente if prospecto.planificacion_prospecto else None
        
        if not prospecto.evaluacion_riesgo:
            raise Exception('No se puede armar el estudio del condominio con datos incompletos, falta la evaluacion de riesgo')
        
        if not prospecto.evaluacion_riesgo.uf_por_metro_cuadrado:
            raise Exception('No se puede armar el estudio del condominio con datos incompletos, falta la uf por metro cuadrado')
        
        if not prospecto.metros_cuadrados:
            raise Exception('No se puede armar el estudio del condominio con datos incompletos, faltan los metros cuadrados')
        
        if prospecto.evaluacion_riesgo.porcentaje_depreciacion is None:
            raise Exception('No se puede armar el estudio del condominio con datos incompletos, falta el porcentaje de depreciación')
        
        if not prospecto.evaluacion_riesgo.porcentaje_espacios_comunes:
            raise Exception('No se puede armar el estudio del condominio con datos incompletos, falta el porcentaje de espacios comunes')
        
        if len(prospecto.evaluacion_riesgo.cotizaciones) == 0:
            raise Exception('No se puede armar el estudio del condominio con datos incompletos, debe tener al menos una cotización')
        
        return self.__armar_estudio(
            monto_asegurado_actual=monto_asegurado_actual,
            infraseguro_primer_ejemplo=infraseguro_primer_ejemplo,
            infraseguro_segundo_ejemplo=infraseguro_segundo_ejemplo,
            metros_cuadrados_construidos=prospecto.metros_cuadrados,
            valor_uf_por_metro_cuadrado=prospecto.evaluacion_riesgo.uf_por_metro_cuadrado,
            porcentaje_depreciacion=prospecto.evaluacion_riesgo.porcentaje_depreciacion,
            cantidad_cuotas=cantidad_cuotas,
            porcentaje_bienes_espacios_comunes=prospecto.evaluacion_riesgo.porcentaje_espacios_comunes,
            cotizaciones=prospecto.evaluacion_riesgo.cotizaciones
        )


    def __armar_estudio(
        self,
        monto_asegurado_actual: float | None,
        infraseguro_primer_ejemplo: float,
        infraseguro_segundo_ejemplo: float,
        metros_cuadrados_construidos: float,
        valor_uf_por_metro_cuadrado: float,
        porcentaje_depreciacion: float,
        cantidad_cuotas: int,
        porcentaje_bienes_espacios_comunes: float,
        cotizaciones: list[Cotizacion]

    ) -> EstudioComercialCondominio:
        
        valor_total_reconstruccion_iva = round(metros_cuadrados_construidos * valor_uf_por_metro_cuadrado * (1 + ArmarEstudioComercialCondominioUseCase.factor_iva))
        valor_total_reconstruccion_depreciacion_iva = round((1 - porcentaje_depreciacion) * valor_total_reconstruccion_iva)
        monto_asegurado_sugerido = round(valor_total_reconstruccion_depreciacion_iva * porcentaje_bienes_espacios_comunes)
        
        infraseguro_actual = None

        if monto_asegurado_actual is not None:
            infraseguro_actual = round(1 - (monto_asegurado_actual / monto_asegurado_sugerido), 2)
        
        monto_asegurado_primer_ejemplo = round(monto_asegurado_sugerido * (1 - infraseguro_primer_ejemplo))
        monto_asegurado_segundo_ejemplo = round(monto_asegurado_sugerido * (1 - infraseguro_segundo_ejemplo))

        detalles: list[DetalleEstudioComercial] = []

        print(f'monto asegurado actual: {monto_asegurado_actual}')
        print(f'infraseguro actual: {infraseguro_actual}')

        for cotizacion in cotizaciones:

            detalle_monto_asegurado_sugerido = self.__detalle_estudio(
                cotizacion=cotizacion,
                monto_asegurado=monto_asegurado_sugerido,
                porcentaje_infraseguro=0
            )

            if monto_asegurado_actual is not None and infraseguro_actual is not None:
                detalle_monto_asegurado_actual = self.__detalle_estudio(
                    cotizacion=cotizacion,
                    monto_asegurado=monto_asegurado_actual,
                    porcentaje_infraseguro=infraseguro_actual
                )
                detalles.append(detalle_monto_asegurado_actual)

            detalle_monto_asegurado_primer_ejemplo = self.__detalle_estudio(
                cotizacion=cotizacion,
                monto_asegurado=monto_asegurado_primer_ejemplo,
                porcentaje_infraseguro=infraseguro_primer_ejemplo
            )

            detalle_monto_asegurado_segundo_ejemplo = self.__detalle_estudio(
                cotizacion=cotizacion,
                monto_asegurado=monto_asegurado_segundo_ejemplo,
                porcentaje_infraseguro=infraseguro_segundo_ejemplo
            )

            detalles.append(detalle_monto_asegurado_sugerido)
            detalles.append(detalle_monto_asegurado_primer_ejemplo)
            detalles.append(detalle_monto_asegurado_segundo_ejemplo)

        estudio = EstudioComercialCondominio(
            cantidad_cuotas=cantidad_cuotas,
            valor_uf=40000,
            detalles=detalles,
            monto_asegurado_actual=monto_asegurado_actual,
            porcentaje_infrasegurdo=infraseguro_actual
        )

        return estudio
    
    
    #######################################
    def __detalle_estudio(self, cotizacion: Cotizacion, monto_asegurado: float, porcentaje_infraseguro: float) -> DetalleEstudioComercial:

        decimales = 2
        tasa_afecta = cotizacion.tasa_afecta
        tasa_excenta = cotizacion.tasa_excenta
        tasa_politica = cotizacion.tasa_politica
        prima_afecta_adicional = cotizacion.prima_adicional_asistencia
        prima_excenta_adicional = 0

        #tasa_bruta = tasa_afecta + tasa_excenta + tasa_politica
        prima_afecta = round((monto_asegurado * tasa_afecta / 1000) + (monto_asegurado * tasa_politica / 1000) + prima_afecta_adicional, decimales)
        prima_excenta = round((monto_asegurado * tasa_excenta / 1000) + prima_excenta_adicional, decimales)
        iva_prima_afecta = round(prima_afecta * ArmarEstudioComercialCondominioUseCase.factor_iva, decimales)
        prima_neta = round(prima_afecta + prima_excenta, decimales)
        prima_bruta = round(prima_neta + iva_prima_afecta, decimales)

        return DetalleEstudioComercial(
            cotizacion=cotizacion,
            monto_asegurado=monto_asegurado,
            porcentaje_infraseguro=porcentaje_infraseguro,
            iva_prima_afecta=iva_prima_afecta,
            prima_neta=prima_neta,
            prima_bruta=prima_bruta
        )