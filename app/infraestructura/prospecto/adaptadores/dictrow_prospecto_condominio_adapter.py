from psycopg.rows import DictRow

from app.dominio.administrador_condominio.administrador_condominio import AdministradorCondominio
from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.planificacion_prospecto.planificacion_prospecto import PlanificacionProspecto
from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio
from app.dominio.usuario.usuario import Usuario


class DictRowProspectoCondominioAdapter:

    def __init__(self, row: DictRow):
        self.row = row

    def to_prospecto_condominio(self) -> ProspectoCondominio:
        id = self.row['id_prospecto']
        id_cliente = self.row['id_cliente']
        id_administrador = self.row['id_administrador']
        nombre_administrador = self.row['nombre_administrador']
        nombre_contacto = self.row['nombre_contacto']
        telefono_administrador = self.row['telefono_administrador']
        correo_administrador = self.row['correo_administrador']
        materialidad = self.row['materialidad']
        clasificacion_preliminar_incendio = self.row['clasificacion_preliminar_incendio']
        procesos_productivos = self.row['procesos_productivos']
        ubicacion_piscina = self.row['ubicacion_piscina']
        tiene_alarma_incendio = self.row['tiene_alarma_incendio']
        tiene_sprinklers = self.row['tiene_sprinklers']
        rut_riesgo = self.row['rut_riesgo']
        nombre_riesgo = self.row['nombre_riesgo']
        telefono_contacto = self.row['telefono_contacto']
        direccion = self.row['direccion']
        correo_contacto = self.row['correo_contacto']
        observaciones = self.row['observaciones']
        nombre_linea_negocio = self.row['linea_negocio']
        rut_registrado_por = self.row['rut_registrado_por']
        nombre_registrado_por = self.row['nombre_registrado_por']
        rut_ej_comercial_asignado = self.row['rut_ej_comercial_asignado']
        nombre_ej_comercial_asignado = self.row['nombre_ej_comercial_asignado']
        id_linea_negocio = self.row['id_linea_negocio']  
        region = self.row['region']  
        comuna = self.row['comuna']  
        informacion_completa = self.row['informacion_completa']
        tiene_locales_comerciales = self.row['tiene_locales_comerciales']
        uso_del_condominio = self.row['uso_del_condominio']
        numero_pisos = self.row['numero_pisos']
        numero_torres = self.row['numero_torres']
        cantidad_departamentos = self.row['cantidad_departamentos']
        cantidad_subterraneos = self.row['cantidad_subterraneos']
        tiene_piscina = self.row['tiene_piscina']
        year_construccion = self.row['year_construccion']
        metros_cuadrados = self.row['metros_cuadrados']
        prospecto_updated_at = self.row['prospecto_updated_at']
        condominio_updated_at = self.row['condominio_updated_at']

        ultima_actualizacion = max(prospecto_updated_at, condominio_updated_at)

        id_company_planificacion = self.row['id_company_planificacion']
        nombre_company_planificacion = self.row['nombre_company_planificacion']
        prima_vigente_planificacion = self.row['prima_vigente_planificacion']
        termino_vigencia_planificacion = self.row['termino_vigencia_planificacion']
        monto_asegurado_vigente_planificacion = self.row['monto_asegurado_vigente_planificacion']
        fecha_envio_cotizacion_planificacion = self.row['fecha_envio_cotizacion_planificacion']

        uf_por_metro_cuadrado = self.row['uf_por_metro_cuadrado']
        porcentaje_depreciacion = self.row['porcentaje_depreciacion']
        porcentaje_espacios_comunes = self.row['porcentaje_espacios_comunes']

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

        ejecutivo_comercial = None

        if rut_ej_comercial_asignado is not None:
            ejecutivo_comercial = Usuario(
                rut = rut_ej_comercial_asignado,
                nombre = nombre_ej_comercial_asignado
            ) 

        administrador = None

        if id_administrador is not None:
            administrador = AdministradorCondominio(
                id=id_administrador,
                nombre_administrador=nombre_administrador,
                nombre_contacto=nombre_contacto,
                telefono=telefono_administrador,
                correo=correo_administrador
            )

        return ProspectoCondominio(
            id = id,
            administrador=administrador,
            id_cliente=id_cliente,
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
            ejecutivo_comercial_asignado=ejecutivo_comercial,
            planificacion_prospecto=planificacion,
            materialidad=materialidad,
            clasificacion_preliminar_incendio=clasificacion_preliminar_incendio,
            procesos_productivos=procesos_productivos,
            ubicacion_piscina=ubicacion_piscina,
            tiene_alarma_incendio=tiene_alarma_incendio,
            tiene_sprinklers=tiene_sprinklers,
            tiene_locales_comerciales=tiene_locales_comerciales,
            uso_del_condominio=uso_del_condominio,
            numero_pisos=numero_pisos,
            numero_torres=numero_torres,
            cantidad_departamentos=cantidad_departamentos,
            cantidad_subterraneos=cantidad_subterraneos,
            tiene_piscina=tiene_piscina,
            year_construccion=year_construccion,
            metros_cuadrados=metros_cuadrados,
            uf_por_metro_cuadrado=uf_por_metro_cuadrado,
            porcentaje_depreciacion=porcentaje_depreciacion,
            porcentaje_espacios_comunes=porcentaje_espacios_comunes,
            ultima_actualizacion=ultima_actualizacion,
            informacion_completa=informacion_completa
        )