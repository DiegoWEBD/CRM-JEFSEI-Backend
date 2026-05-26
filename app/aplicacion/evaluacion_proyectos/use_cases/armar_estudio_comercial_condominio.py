from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from pathlib import Path
from datetime import datetime

from app.dominio.company_seguros.repositorio_company_seguros import RepositorioCompanySeguros
from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.estudio_comercial.detalle_estudio_comercial.detalle_estudio_comercial import DetalleEstudioComercial
from app.dominio.estudio_comercial.estudio_comercial_condominio.estudio_comercial_condominio import EstudioComercialCondominio
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.infraestructura.lib.convertir_numero_a_formato_chileno import convertir_numero_a_formato_chileno


class ArmarEstudioComercialCondominioUseCase:
    factor_iva: float = 0.19

    def __init__(
        self,
        repositorio_prospectos: RepositorioProspectos,
        repositorio_company_seguros: RepositorioCompanySeguros
    ):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_company_seguros = repositorio_company_seguros
        self.datos_plantilla: dict[str, object] = {}
        self.doc = DocxTemplate('app/infraestructura/templates/Plantilla Estudio Condominio.docx')

    def ejecutar(
        self,
        id_prospecto: int,
        infraseguro_primer_ejemplo: float,
        infraseguro_segundo_ejemplo: float,
        cantidad_cuotas: int
    ) -> EstudioComercialCondominio:

        prospecto = self.repositorio_prospectos.buscar_prospecto_condominio(id_prospecto)

        if not prospecto or prospecto.id is None:
            raise ValueError('Prospecto no encontrado')
        
        monto_asegurado_actual = prospecto.planificacion_prospecto.monto_asegurado_vigente if prospecto.planificacion_prospecto else None
        
        if not prospecto.evaluacion_riesgo:
            raise Exception('No se puede armar el estudio del condominio con datos incompletos, falta la evaluacion de riesgo')
        
        if not prospecto.year_construccion:
            raise Exception('No se puede armar el estudio del condominio con datos incompletos, falta el año de construcción del condominio')

        if not prospecto.evaluacion_riesgo.uf_por_metro_cuadrado:
            raise Exception('No se puede armar el estudio del condominio con datos incompletos, falta la uf por metro cuadrado')
        
        if not prospecto.metros_cuadrados:
            raise Exception('No se puede armar el estudio del condominio con datos incompletos, faltan los metros cuadrados')
        
        if not prospecto.cantidad_departamentos:
            raise Exception('No se puede armar el estudio del condominio con datos incompletos, falta la cantidad de unidades')
        
        if prospecto.evaluacion_riesgo.porcentaje_depreciacion is None:
            raise Exception('No se puede armar el estudio del condominio con datos incompletos, falta el porcentaje de depreciación')
        
        if not prospecto.evaluacion_riesgo.porcentaje_espacios_comunes:
            raise Exception('No se puede armar el estudio del condominio con datos incompletos, falta el porcentaje de espacios comunes')
        
        if len(prospecto.evaluacion_riesgo.cotizaciones) == 0:
            raise Exception('No se puede armar el estudio del condominio con datos incompletos, debe tener al menos una cotización')
        
        self.datos_plantilla = {
            'nombre_administrador': prospecto.nombre_contacto,
            'nombre_condominio': prospecto.nombre_riesgo,
            'metros_cuadrados': convertir_numero_a_formato_chileno(prospecto.metros_cuadrados),
            'year_construccion': prospecto.year_construccion,
            'cantidad_unidades': 120, # Falta implementar el campo cantidad_unidades en la tabla Prospecto y sus relacionadas
            'direccion': prospecto.direccion,
            'comuna': prospecto.comuna.nombre,
            'uf_por_metro_cuadrado': convertir_numero_a_formato_chileno(prospecto.evaluacion_riesgo.uf_por_metro_cuadrado),
            'porcentaje_depreciacion': round(prospecto.evaluacion_riesgo.porcentaje_depreciacion * 100),
            'porcentaje_espacios_comunes': round(prospecto.evaluacion_riesgo.porcentaje_espacios_comunes * 100),
            'cantidad_cuotas': cantidad_cuotas,
            'year_actual': datetime.now().year
        }

        estudio = self.__armar_estudio(
            id_prospecto=prospecto.id,
            monto_asegurado_actual=monto_asegurado_actual,
            infraseguro_primer_ejemplo=infraseguro_primer_ejemplo,
            infraseguro_segundo_ejemplo=infraseguro_segundo_ejemplo,
            metros_cuadrados_construidos=prospecto.metros_cuadrados,
            valor_uf_por_metro_cuadrado=prospecto.evaluacion_riesgo.uf_por_metro_cuadrado,
            porcentaje_depreciacion=prospecto.evaluacion_riesgo.porcentaje_depreciacion,
            cantidad_cuotas=cantidad_cuotas,
            cantidad_unidades=120,
            porcentaje_bienes_espacios_comunes=prospecto.evaluacion_riesgo.porcentaje_espacios_comunes,
            cotizaciones=prospecto.evaluacion_riesgo.cotizaciones
        )

        return estudio
    

    def __armar_estudio(
        self,
        id_prospecto: int,
        monto_asegurado_actual: float | None,
        infraseguro_primer_ejemplo: float,
        infraseguro_segundo_ejemplo: float,
        metros_cuadrados_construidos: float,
        valor_uf_por_metro_cuadrado: float,
        porcentaje_depreciacion: float,
        cantidad_cuotas: int,
        cantidad_unidades: int,
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

        self.datos_plantilla.update({
            'valor_reconstruccion': convertir_numero_a_formato_chileno(valor_total_reconstruccion_iva),
            'valor_reconstruccion_depreciacion': convertir_numero_a_formato_chileno(valor_total_reconstruccion_depreciacion_iva),
            'monto_asegurado_sugerido': convertir_numero_a_formato_chileno(monto_asegurado_sugerido)
        })

        detalles: list[DetalleEstudioComercial] = []
        detalles_monto_asegurado_actual: list[DetalleEstudioComercial] = []
        detalles_monto_asegurado_primer_ejemplo: list[DetalleEstudioComercial] = []
        detalles_monto_asegurado_segundo_ejemplo: list[DetalleEstudioComercial] = []
        detalles_monto_asegurado_sugerido: list[DetalleEstudioComercial] = []

        for cotizacion in cotizaciones:

            # Monto asegurado sugerido
            detalle_monto_asegurado_sugerido = self.__detalle_estudio(
                cotizacion=cotizacion,
                monto_asegurado=monto_asegurado_sugerido,
                porcentaje_infraseguro=0,
                cantidad_cuotas=cantidad_cuotas
            )

            detalles.append(detalle_monto_asegurado_sugerido)
            detalles_monto_asegurado_sugerido.append(detalle_monto_asegurado_sugerido)

            # Monto asegurado actual
            if monto_asegurado_actual is not None and infraseguro_actual is not None:
                detalle_monto_asegurado_actual = self.__detalle_estudio(
                    cotizacion=cotizacion,
                    monto_asegurado=monto_asegurado_actual,
                    porcentaje_infraseguro=infraseguro_actual,
                    cantidad_cuotas=cantidad_cuotas
                )
                
                self.datos_plantilla.update({
                    'monto_asegurado_actual': convertir_numero_a_formato_chileno(monto_asegurado_actual),
                    'porcentaje_infraseguro_actual': round(infraseguro_actual * 100)
                })

                detalles.append(detalle_monto_asegurado_actual)
                detalles_monto_asegurado_actual.append(detalle_monto_asegurado_actual)

            # Monto asegurado primer ejemplo infraseguro
            detalle_monto_asegurado_primer_ejemplo = self.__detalle_estudio(
                cotizacion=cotizacion,
                monto_asegurado=monto_asegurado_primer_ejemplo,
                porcentaje_infraseguro=infraseguro_primer_ejemplo,
                cantidad_cuotas=cantidad_cuotas
            )

            self.datos_plantilla.update({
                'monto_asegurado_primer_ejemplo': convertir_numero_a_formato_chileno(monto_asegurado_primer_ejemplo),
                'porcentaje_infraseguro_primer_ejemplo': round(infraseguro_primer_ejemplo * 100)
            })

            detalles.append(detalle_monto_asegurado_primer_ejemplo)
            detalles_monto_asegurado_primer_ejemplo.append(detalle_monto_asegurado_primer_ejemplo)

            # Monto asegurado segundo ejemplo infraseguro
            detalle_monto_asegurado_segundo_ejemplo = self.__detalle_estudio(
                cotizacion=cotizacion,
                monto_asegurado=monto_asegurado_segundo_ejemplo,
                porcentaje_infraseguro=infraseguro_segundo_ejemplo,
                cantidad_cuotas=cantidad_cuotas
            )

            self.datos_plantilla.update({
                'monto_asegurado_segundo_ejemplo': convertir_numero_a_formato_chileno(monto_asegurado_segundo_ejemplo),
                'porcentaje_infraseguro_segundo_ejemplo': round(infraseguro_segundo_ejemplo * 100)
            })

            detalles.append(detalle_monto_asegurado_segundo_ejemplo)
            detalles_monto_asegurado_segundo_ejemplo.append(detalle_monto_asegurado_segundo_ejemplo)


        estudio = EstudioComercialCondominio(
            cantidad_cuotas=cantidad_cuotas,
            valor_uf=40000,
            detalles=detalles,
            monto_asegurado_actual=monto_asegurado_actual,
            porcentaje_infrasegurdo=infraseguro_actual
        )

        self.__renderizar_detalles_docx(detalles_monto_asegurado_actual, cantidad_unidades, 'detalles_monto_asegurado_actual')
        self.__renderizar_detalles_docx(detalles_monto_asegurado_primer_ejemplo, cantidad_unidades, 'detalles_monto_asegurado_primer_ejemplo')
        self.__renderizar_detalles_docx(detalles_monto_asegurado_segundo_ejemplo, cantidad_unidades, 'detalles_monto_asegurado_segundo_ejemplo')
        self.__renderizar_detalles_docx(detalles_monto_asegurado_sugerido, cantidad_unidades, 'detalles_monto_asegurado_sugerido')

        nombre_estudio = f'estudio_comercial_condominio_id_{id_prospecto}'

        carpeta_estudio = Path( f'documentos/estudios/{nombre_estudio}')

        # crea toda la ruta si no existe
        carpeta_estudio.mkdir(parents=True, exist_ok=True)

        ruta_docx = carpeta_estudio / f'{nombre_estudio}.docx'

        self.doc.render(self.datos_plantilla)

        self.doc.save(ruta_docx)

        return estudio
    
    
    def __detalle_estudio(
        self, 
        cotizacion: Cotizacion, 
        monto_asegurado: float, 
        porcentaje_infraseguro: float,
        cantidad_cuotas: int
    ) -> DetalleEstudioComercial:

        decimales = 2
        tasa_afecta = cotizacion.tasa_afecta
        tasa_excenta = cotizacion.tasa_excenta
        tasa_politica = cotizacion.tasa_politica
        prima_afecta_adicional = cotizacion.prima_adicional_asistencia
        prima_excenta_adicional = 0

        prima_afecta = round((monto_asegurado / 1000 * (tasa_afecta + tasa_politica)) + prima_afecta_adicional, decimales)
        prima_excenta = round((monto_asegurado * tasa_excenta / 1000) + prima_excenta_adicional, decimales)
        iva_prima_afecta = round(prima_afecta * ArmarEstudioComercialCondominioUseCase.factor_iva, decimales)
        prima_neta = round(prima_afecta + prima_excenta, decimales)
        prima_bruta = round(prima_neta + iva_prima_afecta, decimales)

        factores_cuotas = self.repositorio_company_seguros.obtener_factores_cuotas(cotizacion.company.id)
        factor = None

        for factor_cuota in factores_cuotas:
            if factor_cuota.numero_cuotas == cantidad_cuotas:
                factor = factor_cuota.factor

        if factor is not None:
            valor_cuota = prima_bruta * factor
        else:
            valor_cuota = self.__valor_cuota_con_factor_generico(
                cantidad_cuotas=cantidad_cuotas,
                prima_bruta=prima_bruta
            )

        return DetalleEstudioComercial(
            cotizacion=cotizacion,
            monto_asegurado=monto_asegurado,
            porcentaje_infraseguro=porcentaje_infraseguro,
            iva_prima_afecta=iva_prima_afecta,
            prima_neta=prima_neta,
            prima_bruta=prima_bruta,
            valor_cuota=round(valor_cuota, decimales)
        )
    
    def __valor_cuota_con_factor_generico(self, cantidad_cuotas: int, prima_bruta: float) -> float:
        tasa = 0.005      # 0.5%

        cuota = (tasa * prima_bruta) / (1 - (1 + tasa) ** -cantidad_cuotas)
        return cuota
    
    def __renderizar_detalles_docx(self, detalles: list[DetalleEstudioComercial], cantidad_unidades: int, dict_key: str):
        datos_detalles = []
        VALOR_UF = 40509.29

        for detalle in detalles:
            valor_cuota_pesos = round(detalle.valor_cuota * VALOR_UF)
            prorrateo_pesos = round(valor_cuota_pesos / cantidad_unidades)

            logo = InlineImage(
                self.doc,
                f'app/infraestructura/logos/companies/company_{detalle.cotizacion.company.id}.png',
                width=Mm(25)
            )

            datos_detalles.append({
                'logo': logo,
                'nombre_company': detalle.cotizacion.company.nombre,
                'monto_asegurado': convertir_numero_a_formato_chileno(detalle.monto_asegurado),
                'prima_anual': convertir_numero_a_formato_chileno(detalle.prima_bruta),
                'valor_cuota_uf': convertir_numero_a_formato_chileno(detalle.valor_cuota),
                'valor_cuota_pesos': convertir_numero_a_formato_chileno(valor_cuota_pesos),
                'prorrateo_pesos': convertir_numero_a_formato_chileno(prorrateo_pesos)
            })

        self.datos_plantilla[dict_key] = datos_detalles
