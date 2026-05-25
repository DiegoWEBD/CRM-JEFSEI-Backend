from psycopg.rows import DictRow

from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.comuna.comuna import Comuna
from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.estudio_comercial.detalle_estudio_comercial.detalle_estudio_comercial import DetalleEstudioComercial
from app.dominio.estudio_comercial.estudio_comercial_condominio.estudio_comercial_condominio import EstudioComercialCondominio
from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo
from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.planificacion_prospecto.planificacion_prospecto import PlanificacionProspecto
from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio
from app.dominio.solicitud_evaluacion_riesgo.solicitud_evaluacion_riesgo import SolicitudEvaluacionRiesgo
from app.dominio.usuario.usuario import Usuario


class TupleRowsProspectoCondominioAdapter:
    
    def __init__(self, rows: list[DictRow]):

        if not rows or len(rows) == 0:
            raise Exception("Prospecto inválido")
        
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
        nombre_comuna = self.rows[0]['comuna']  
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

        id_company_planificacion = self.rows[0]['id_company_planificacion']
        nombre_company_planificacion = self.rows[0]['nombre_company_planificacion']
        prima_vigente_planificacion = self.rows[0]['prima_vigente_planificacion']
        termino_vigencia_planificacion = self.rows[0]['termino_vigencia_planificacion']
        monto_asegurado_vigente_planificacion = self.rows[0]['monto_asegurado_vigente_planificacion']
        fecha_envio_cotizacion_planificacion = self.rows[0]['fecha_envio_cotizacion_planificacion']

        id_solicitud_evaluacion = self.rows[0]['id_solicitud_evaluacion']
        fecha_solicitud_evaluacion = self.rows[0]['fecha_solicitud_evaluacion']
        prioridad_solicitud = self.rows[0]['prioridad_solicitud']

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

        comuna = Comuna(
            nombre = nombre_comuna
        )

        linea_negocio = LineaNegocio(
            nombre=nombre_linea_negocio,
            productos=[]
        )

        registrado_por = Usuario(
            rut = rut_registrado_por,
            nombre = nombre_registrado_por
        )

        ej_comercial = None
        ej_evaluacion = None
        solicitud_evaluacion = None

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

        if id_solicitud_evaluacion:
            solicitud_evaluacion = SolicitudEvaluacionRiesgo(
                id=id_solicitud_evaluacion,
                prioridad=prioridad_solicitud,
                fecha_solicitud=fecha_solicitud_evaluacion
            )

        prospecto = ProspectoCondominio(
            id = id,
            rut_riesgo = rut_riesgo,
            nombre_riesgo = nombre_riesgo,
            telefono_contacto = telefono_contacto,
            correo_contacto = correo_contacto,
            direccion = direccion,
            comuna = comuna,
            observaciones = observaciones,
            linea_negocio=linea_negocio,
            registrado_por=registrado_por,
            ejecutivo_comercial_asignado=ej_comercial,
            ejecutivo_evaluacion_asignado=ej_evaluacion,
            companies_sugeridas=[],
            nombre_contacto=nombre_contacto,
            cargo_contacto=cargo_contacto,
            historial_estados=[],
            planificacion_prospecto=planificacion,
            solicitud_evaluacion_riesgo=solicitud_evaluacion,
            tiene_locales_comerciales=tiene_locales_comerciales,
            uso_del_condominio=uso_del_condominio,
            numero_pisos=numero_pisos,
            numero_torres=numero_torres,
            cantidad_departamentos=cantidad_departamentos,
            cantidad_subterraneos=cantidad_subterraneos,
            tiene_piscina=tiene_piscina,
            year_construccion=year_construccion,
            metros_cuadrados=metros_cuadrados,
            desea_ser_contactado=desea_ser_contactado
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

        if evaluacion_riesgo is None:
            return prospecto

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

        evaluacion_riesgo.cotizaciones = cotizaciones

        if id_estudio_comercial is not None:
            estudio = EstudioComercialCondominio(
                cantidad_cuotas=cantidad_cuotas,
                valor_uf=valor_uf,
                detalles=detalles_estudio
            )
            evaluacion_riesgo.estudio = estudio

        prospecto.evaluacion_riesgo = evaluacion_riesgo

        return prospecto

'''
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
        nombre_comuna = self.rows[0]['comuna']  
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

        id_company_planificacion = self.rows[0]['id_company_planificacion']
        nombre_company_planificacion = self.rows[0]['nombre_company_planificacion']
        prima_vigente_planificacion = self.rows[0]['prima_vigente_planificacion']
        termino_vigencia_planificacion = self.rows[0]['termino_vigencia_planificacion']
        monto_asegurado_vigente_planificacion = self.rows[0]['monto_asegurado_vigente_planificacion']
        fecha_envio_cotizacion_planificacion = self.rows[0]['fecha_envio_cotizacion_planificacion']

        id_solicitud_evaluacion = self.rows[0]['id_solicitud_evaluacion']
        fecha_solicitud_evaluacion = self.rows[0]['fecha_solicitud_evaluacion']
        prioridad_solicitud = self.rows[0]['prioridad_solicitud']

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

        comuna = Comuna(
            nombre = nombre_comuna
        )

        linea_negocio = LineaNegocio(
            nombre=nombre_linea_negocio,
            productos=[]
        )

        registrado_por = Usuario(
            rut = rut_registrado_por,
            nombre = nombre_registrado_por
        )

        ej_comercial = None
        ej_evaluacion = None
        solicitud_evaluacion = None
        evaluacion_riesgo = None

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

        if id_solicitud_evaluacion:
            solicitud_evaluacion = SolicitudEvaluacionRiesgo(
                id=id_solicitud_evaluacion,
                prioridad=prioridad_solicitud,
                fecha_solicitud=fecha_solicitud_evaluacion
            )

        if id_evaluacion:
            evaluacion_riesgo = EvaluacionRiesgo(
                id = id_evaluacion,
                uf_por_metro_cuadrado=evaluacion_uf_por_metro_cuadrado,
                porcentaje_depreciacion=evaluacion_porcentaje_depreciacion,
                porcentaje_espacios_comunes=evaluacion_porcentaje_espacios_comunes,
                observaciones=observaciones_evaluacion
            )

        historial_estados: list[HistorialEstado] = []

        for row in self.rows:
            nombre_estado_actual = row['nombre_estado_actual']
            codigo_estado_actual = row['codigo_estado_actual']
            color_estado_actual = row['color_estado_actual']
            fecha_registro_estado = row['fecha_registro_estado']
            motivo_cambio_estado = row['motivo_cambio_estado']
            rut_estado_cambiado_por = row['rut_estado_cambiado_por']
            nombre_estado_cambiado_por = row['nombre_estado_cambiado_por']
            dias_limite_particular = row['dias_limite_particular']
            dias_limite_base = row['dias_limite_base']
            codigo_siguiente_estado_esperado = row['codigo_siguiente_estado_esperado']
            nombre_siguiente_estado_esperado = row['nombre_siguiente_estado_esperado']
            proxima_accion_esperada = row['proxima_accion_esperada']
            codigo_estado_anterior = row['codigo_estado_anterior']
            nombre_estado_anterior = row['nombre_estado_anterior']
            dias_transcurridos = row['dias_transcurridos']

            estado_cambiado_por = Usuario(
                rut=rut_estado_cambiado_por,
                nombre=nombre_estado_cambiado_por
            )

            estado_particular_anterior = None

            if codigo_estado_anterior:
                estado_base_anterior = EstadoBase(
                    codigo=codigo_estado_anterior,
                    nombre=nombre_estado_anterior,
                    dias_limite=0 # arbitrario
                )

                estado_particular_anterior = EstadoParticular(
                    estado_base=estado_base_anterior,
                    dias_limite_particular=None
                )

            estado_base_actual = EstadoBase(
                codigo=codigo_estado_actual,
                nombre=nombre_estado_actual,
                dias_limite=dias_limite_base,
                color=color_estado_actual
            )

            siguiente_estado_base_esperado = EstadoBase(
                codigo=codigo_siguiente_estado_esperado,
                nombre=nombre_siguiente_estado_esperado,
                accion=proxima_accion_esperada,
                dias_limite=0 # arbitrario
            )

            estado_base_actual.siguiente_estado = siguiente_estado_base_esperado

            estado_particular_actual = EstadoParticular(
                estado_base=estado_base_actual,
                dias_limite_particular=dias_limite_particular
            )

            historial_estado = HistorialEstado(
                estado_anterior=estado_particular_anterior,
                estado_actual=estado_particular_actual,
                dias_transcurridos=dias_transcurridos,
                fecha_registro=fecha_registro_estado,
                cambiado_por=estado_cambiado_por,
                motivo_cambio=motivo_cambio_estado
            )

            historial_estados.append(historial_estado)

        return ProspectoCondominio(
            id = id,
            rut_riesgo = rut_riesgo,
            nombre_riesgo = nombre_riesgo,
            telefono_contacto = telefono_contacto,
            correo_contacto = correo_contacto,
            direccion = direccion,
            comuna = comuna,
            observaciones = observaciones,
            linea_negocio=linea_negocio,
            registrado_por=registrado_por,
            ejecutivo_comercial_asignado=ej_comercial,
            ejecutivo_evaluacion_asignado=ej_evaluacion,
            companies_sugeridas=[],
            nombre_contacto=nombre_contacto,
            cargo_contacto=cargo_contacto,
            historial_estados=historial_estados,
            planificacion_prospecto=planificacion,
            solicitud_evaluacion_riesgo=solicitud_evaluacion,
            evaluacion_riesgo=evaluacion_riesgo,
            tiene_locales_comerciales=tiene_locales_comerciales,
            uso_del_condominio=uso_del_condominio,
            numero_pisos=numero_pisos,
            numero_torres=numero_torres,
            cantidad_departamentos=cantidad_departamentos,
            cantidad_subterraneos=cantidad_subterraneos,
            tiene_piscina=tiene_piscina,
            year_construccion=year_construccion,
            metros_cuadrados=metros_cuadrados,
            desea_ser_contactado=desea_ser_contactado
        )
'''