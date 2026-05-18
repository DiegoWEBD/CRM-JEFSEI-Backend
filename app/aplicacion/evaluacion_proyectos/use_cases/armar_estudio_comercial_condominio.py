from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.company_seguros.repositorio_company_seguros import RepositorioCompanySeguros
from app.dominio.estudio_comercial.detalle_estudio_comercial.detalle_estudio_comercial import DetalleEstudioComercial
from app.dominio.estudio_comercial.estudio_comercial_condominio.estudio_comercial_condominio import EstudioComercialCondominio
from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio
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
        cantidad_cuotas: int,
        id_companies: list[int]
    ) -> EstudioComercialCondominio:

        companies: list[CompanySeguros] = []

        for id_company in id_companies:
            company = self.repositorio_company_seguros.buscar(id_company)

            if not company:
                raise ValueError(f"Companía (ID: {id_company}) no encontrada")
            
            companies.append(company)

        prospecto = self.repositorio_prospectos.buscar_prospecto_condominio(id_prospecto)

        if not prospecto:
            raise ValueError('Prospecto no encontrado')
        
        monto_asegurado_actual = prospecto.planificacion_prospecto.monto_asegurado_vigente if prospecto.planificacion_prospecto else None
        
        if not prospecto.evaluacion_riesgo:
            raise Exception('No se puede armar el estudio del condominio con datos incompletos')
        
        if not prospecto.evaluacion_riesgo.uf_por_metro_cuadrado:
            raise Exception('No se puede armar el estudio del condominio con datos incompletos')
        
        if not prospecto.metros_cuadrados:
            raise Exception('No se puede armar el estudio del condominio con datos incompletos')
        
        if not prospecto.evaluacion_riesgo.uf_por_metro_cuadrado:
            raise Exception('No se puede armar el estudio del condominio con datos incompletos')
        
        if not prospecto.evaluacion_riesgo.porcentaje_depreciacion:
            raise Exception('No se puede armar el estudio del condominio con datos incompletos')
        
        if not prospecto.evaluacion_riesgo.porcentaje_espacios_comunes:
            raise Exception('No se puede armar el estudio del condominio con datos incompletos')
        
        return self.__armar_estudio(
            monto_asegurado_actual=monto_asegurado_actual,
            infraseguro_primer_ejemplo=infraseguro_primer_ejemplo,
            infraseguro_segundo_ejemplo=infraseguro_segundo_ejemplo,
            metros_cuadrados_construidos=prospecto.metros_cuadrados,
            valor_uf_por_metro_cuadrado=prospecto.evaluacion_riesgo.uf_por_metro_cuadrado,
            porcentaje_depreciacion=prospecto.evaluacion_riesgo.porcentaje_depreciacion,
            cantidad_cuotas=cantidad_cuotas,
            porcentaje_bienes_espacios_comunes=prospecto.evaluacion_riesgo.porcentaje_espacios_comunes,
            companies=companies
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
        companies: list[CompanySeguros]

    ) -> EstudioComercialCondominio:
        
        valor_total_reconstruccion_iva = round(metros_cuadrados_construidos * valor_uf_por_metro_cuadrado * (1 + ArmarEstudioComercialCondominioUseCase.factor_iva))
        valor_total_reconstruccion_depreciacion_iva = round((1 - porcentaje_depreciacion) * valor_total_reconstruccion_iva)
        monto_asegurado_sugerido = round(valor_total_reconstruccion_depreciacion_iva * porcentaje_bienes_espacios_comunes)
        
        infraseguro_actual = None

        if monto_asegurado_actual:
            infraseguro_actual = round(1 - (monto_asegurado_actual / monto_asegurado_sugerido), 2)
        
        monto_asegurado_primer_ejemplo = round(monto_asegurado_sugerido * (1 - infraseguro_primer_ejemplo))
        monto_asegurado_segundo_ejemplo = round(monto_asegurado_sugerido * (1 - infraseguro_segundo_ejemplo))

        detalles: list[DetalleEstudioComercial] = []

        for company in companies:

            detalle_monto_asegurado_sugerido = self.__detalle_estudio_segun_primas(
                monto_total_asegurado=monto_asegurado_sugerido,
                porcentaje_infraseguro=0,
                prima_afecta=105.62,
                prima_excenta=393.46,
                company=company
            )

            detalle_monto_asegurado_primer_ejemplo = self.__detalle_estudio_segun_primas(
                monto_total_asegurado=monto_asegurado_primer_ejemplo,
                porcentaje_infraseguro=infraseguro_primer_ejemplo,
                prima_afecta=105.62,
                prima_excenta=393.46,
                company=company
            )

            detalle_monto_asegurado_segundo_ejemplo = self.__detalle_estudio_segun_primas(
                monto_total_asegurado=monto_asegurado_segundo_ejemplo,
                porcentaje_infraseguro=infraseguro_segundo_ejemplo,
                prima_afecta=105.62,
                prima_excenta=393.46,
                company=company
            )

            detalles.append(detalle_monto_asegurado_sugerido)
            detalles.append(detalle_monto_asegurado_primer_ejemplo)
            detalles.append(detalle_monto_asegurado_segundo_ejemplo)

        estudio = EstudioComercialCondominio(
            monto_asegurado_actual=monto_asegurado_actual,
            metros_cuadrados_construidos=metros_cuadrados_construidos,
            uf_por_metro_cuadrado=valor_uf_por_metro_cuadrado,
            porcentaje_depreciacion=porcentaje_depreciacion,
            porcentaje_espacios_comunes=porcentaje_bienes_espacios_comunes,
            cantidad_cuotas=cantidad_cuotas,
            valor_uf=40000,
            detalles=detalles
        )

        return estudio
    
    def __detalle_estudio_segun_primas(
        self, 
        monto_total_asegurado: float, 
        porcentaje_infraseguro: float,
        prima_afecta: float, 
        prima_excenta: float,
        company: CompanySeguros
    ) -> DetalleEstudioComercial:

        iva_prima_afecta = prima_afecta * ArmarEstudioComercialCondominioUseCase.factor_iva
        prima_neta = prima_afecta + prima_excenta
        prima_bruta = iva_prima_afecta + prima_neta
        tasa_afecta = (prima_afecta / monto_total_asegurado) * 1000
        tasa_excenta = (prima_excenta / monto_total_asegurado) * 1000
        
        return DetalleEstudioComercial(
            monto_total_asegurado==monto_total_asegurado,
            porcentaje_infraseguro=porcentaje_infraseguro,
            iva_prima_afecta=iva_prima_afecta,
            prima_neta=prima_neta,
            prima_bruta=prima_bruta,
            tasa_afecta=tasa_afecta,
            tasa_excenta=tasa_excenta,
            company=company
        )
    
    #######################################
    def __detalle_estudio_segun_tasas(
        self,
        company: CompanySeguros,
        monto_total_asegurado: float, 
        tasa_afecta: float,
        tasa_excenta: float,
        tasa_politica: float,
        prima_afecta_adicional: float,
        prima_excenta_adicional: float
    ):
        tasa_bruta = tasa_afecta + tasa_excenta + tasa_politica
        prima_afecta = (monto_total_asegurado * tasa_afecta / 1000) + (monto_total_asegurado * tasa_politica / 1000) + prima_afecta_adicional
        prima_excenta = (monto_total_asegurado * tasa_excenta / 1000) + prima_excenta_adicional
        iva_prima_afecta = prima_afecta * ArmarEstudioComercialCondominioUseCase.factor_iva
        prima_bruta = prima_afecta + prima_excenta + iva_prima_afecta