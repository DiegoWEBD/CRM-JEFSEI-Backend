from psycopg.rows import DictRow

from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.estudio_comercial.detalle_estudio_comercial.detalle_estudio_comercial import DetalleEstudioComercial
from app.dominio.estudio_comercial.estudio_comercial_condominio.estudio_comercial_condominio import EstudioComercialCondominio
from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo
from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.planificacion_prospecto.planificacion_prospecto import PlanificacionProspecto
from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial
from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio
from app.dominio.solicitud_cotizacion.solicitud_cotizacion import SolicitudCotizacion
from app.dominio.usuario.usuario import Usuario


class TupleRowsProspectoCondominioAdapter:
    
    def __init__(self, rows: list[DictRow]):

        if not rows or len(rows) == 0:
            raise Exception('Prospecto inválido')
        
        self.rows = rows

    def to_prospecto_condominio(self) -> ProspectoCondominio:

        id = self.rows[0]['id_prospecto']
        rut_riesgo = self.rows[0]['rut_riesgo']
        nombre_riesgo = self.rows[0]['nombre_riesgo']
        telefono_contacto = self.rows[0]['telefono_contacto']
        direccion = self.rows[0]['direccion']
        nombre_contacto = self.rows[0]['nombre_contacto']
        cargo_contacto = self.rows[0]['cargo_contacto']
        correo_contacto = self.rows[0]['correo_contacto']
        observaciones = self.rows[0]['observaciones']
        nombre_linea_negocio = self.rows[0]['linea_negocio']
        rut_registrado_por = self.rows[0]['rut_registrado_por']
        nombre_registrado_por = self.rows[0]['nombre_registrado_por']
        id_linea_negocio = self.rows[0]['id_linea_negocio']  
        region = self.rows[0]['region']  
        comuna = self.rows[0]['comuna']  
        tiene_locales_comerciales = self.rows[0]['tiene_locales_comerciales']
        uso_del_condominio = self.rows[0]['uso_del_condominio']
        numero_pisos = self.rows[0]['numero_pisos']
        numero_torres = self.rows[0]['numero_torres']
        cantidad_departamentos = self.rows[0]['cantidad_departamentos']
        cantidad_subterraneos = self.rows[0]['cantidad_subterraneos']
        tiene_piscina = self.rows[0]['tiene_piscina']
        year_construccion = self.rows[0]['year_construccion']
        metros_cuadrados = self.rows[0]['metros_cuadrados']
        desea_ser_contactado = self.rows[0]['desea_ser_contactado']
        id_proceso_comercial = self.rows[0]['id_proceso_comercial']
        prospecto_updated_at = self.rows[0]['prospecto_updated_at']
        condominio_updated_at = self.rows[0]['condominio_updated_at']

        ultima_actualizacion = max(prospecto_updated_at, condominio_updated_at)

        id_company_planificacion = self.rows[0]['id_company_planificacion']
        nombre_company_planificacion = self.rows[0]['nombre_company_planificacion']
        prima_vigente_planificacion = self.rows[0]['prima_vigente_planificacion']
        termino_vigencia_planificacion = self.rows[0]['termino_vigencia_planificacion']
        monto_asegurado_vigente_planificacion = self.rows[0]['monto_asegurado_vigente_planificacion']
        fecha_envio_cotizacion_planificacion = self.rows[0]['fecha_envio_cotizacion_planificacion']

        id_evaluacion = self.rows[0]['id_evaluacion']
        observaciones_evaluacion = self.rows[0]['observaciones_evaluacion']
        evaluacion_uf_por_metro_cuadrado = self.rows[0]['evaluacion_uf_por_metro_cuadrado']
        evaluacion_porcentaje_depreciacion = self.rows[0]['evaluacion_porcentaje_depreciacion']
        evaluacion_porcentaje_espacios_comunes = self.rows[0]['evaluacion_porcentaje_espacios_comunes']

        rut_ej_comercial = self.rows[0]['rut_ej_comercial']
        nombre_ej_comercial = self.rows[0]['nombre_ej_comercial']
        rut_ej_evaluacion = self.rows[0]['rut_ej_evaluacion']
        nombre_ej_evaluacion = self.rows[0]['nombre_ej_evaluacion']

        planificacion = None

        if id_company_planificacion:

            company_poliza_vigente = CompanySeguros(
                id=id_company_planificacion,
                nombre=nombre_company_planificacion,
                nombre_logo='',
                factores_cuotas=[],
                coberturas=[]
            )

            planificacion = PlanificacionProspecto(
                prima_vigente=prima_vigente_planificacion,
                company_poliza=company_poliza_vigente,
                termino_vigencia=termino_vigencia_planificacion,
                monto_asegurado_vigente=monto_asegurado_vigente_planificacion,
                fecha_envio_cotizacion=fecha_envio_cotizacion_planificacion
            )

        linea_negocio = LineaNegocio(
            id=id_linea_negocio,
            nombre=nombre_linea_negocio,
            productos=[]
        )

        registrado_por = Usuario(
            rut = rut_registrado_por,
            nombre = nombre_registrado_por
        )

        ej_comercial = None
        ej_evaluacion = None
        solicitud_cotizacion = None

        if rut_ej_comercial:
            ej_comercial = Usuario(
                rut = rut_ej_comercial,
                nombre = nombre_ej_comercial
            )

        if rut_ej_evaluacion:
            ej_evaluacion = Usuario(
                rut = rut_ej_evaluacion,
                nombre = nombre_ej_evaluacion
            )   

        evaluacion_riesgo = None

        if id_evaluacion is not None:
            evaluacion_riesgo = EvaluacionRiesgo(
                id = id_evaluacion,
                uf_por_metro_cuadrado=evaluacion_uf_por_metro_cuadrado,
                porcentaje_depreciacion=evaluacion_porcentaje_depreciacion,
                porcentaje_espacios_comunes=evaluacion_porcentaje_espacios_comunes,
                observaciones=observaciones_evaluacion
            )

        estudio = None
        id_estudio_comercial = self.rows[0]['id_estudio_comercial']
        cantidad_cuotas = self.rows[0]['cantidad_cuotas']
        valor_uf = self.rows[0]['valor_uf']

        detalles_estudio: list[DetalleEstudioComercial] = []
        solicitudes_cotizacion: dict[int, SolicitudCotizacion] = {}

        for row in self.rows:
            id_solicitud_cotizacion = row['id_solicitud_cotizacion']

            if id_solicitud_cotizacion is not None and id_solicitud_cotizacion not in solicitudes_cotizacion:

                fecha_solicitud_cotizacion = row['fecha_solicitud_cotizacion']
                prioridad_cotizacion = row['prioridad_cotizacion']

                solicitud_cotizacion = SolicitudCotizacion(
                    id=id_solicitud_cotizacion,
                    fecha=fecha_solicitud_cotizacion,
                    prioridad=prioridad_cotizacion,
                    cotizaciones=[]
                )

                solicitudes_cotizacion[id_solicitud_cotizacion] = solicitud_cotizacion

            id_cotizacion = row['id_cotizacion']

            if id_cotizacion is None:
                continue

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

            solicitudes_cotizacion[id_solicitud_cotizacion].cotizaciones.append(cotizacion)

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
                    prima_bruta=detalle_prima_bruta,
                    monto_asegurado=cotizacion_monto_total_asegurado,
                    valor_cuota=0 # SE DEBE CAMBIAR
                )

                detalles_estudio.append(detalle)

        if id_estudio_comercial is not None:
            estudio = EstudioComercialCondominio(
                cantidad_cuotas=cantidad_cuotas,
                valor_uf=valor_uf,
                monto_asegurado_actual=monto_asegurado_vigente_planificacion,
                porcentaje_infraseguro=0,
                detalles_monto_asegurado_actual=[],
                detalles_monto_asegurado_sugerido=[],
                detalles_monto_asegurado_primer_ejemplo=[],
                detalles_monto_asegurado_segundo_ejemplo=[]
            )

        proceso_comercial = ProcesoComercial(
            id=id_proceso_comercial,
            ejecutivo_comercial=ej_comercial,
            ejecutivo_evaluacion=ej_evaluacion,
            solicitudes_cotizacion=list(solicitudes_cotizacion.values()),
            estudio=estudio,
            poliza=None,
            plan_pago=None,
            historial_estados=[]
        )

        prospecto = ProspectoCondominio(
            id = id,
            proceso_comercial=proceso_comercial,
            rut_riesgo = rut_riesgo,
            nombre_riesgo = nombre_riesgo,
            telefono_contacto = telefono_contacto,
            correo_contacto = correo_contacto,
            direccion = direccion,
            region=region,
            comuna = comuna,
            observaciones = observaciones,
            linea_negocio=linea_negocio,
            registrado_por=registrado_por,
            companies_sugeridas=[],
            nombre_contacto=nombre_contacto,
            cargo_contacto=cargo_contacto,
            planificacion_prospecto=planificacion,
            tiene_locales_comerciales=tiene_locales_comerciales,
            uso_del_condominio=uso_del_condominio,
            numero_pisos=numero_pisos,
            numero_torres=numero_torres,
            cantidad_departamentos=cantidad_departamentos,
            cantidad_subterraneos=cantidad_subterraneos,
            tiene_piscina=tiene_piscina,
            year_construccion=year_construccion,
            metros_cuadrados=metros_cuadrados,
            desea_ser_contactado=desea_ser_contactado,
            evaluacion_riesgo=evaluacion_riesgo,
            ultima_actualizacion=ultima_actualizacion
        )

        return prospecto
