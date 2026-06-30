from psycopg.rows import DictRow

from app.dominio.administrador_condominio.administrador_condominio import AdministradorCondominio
from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.planificacion_prospecto.planificacion_prospecto import PlanificacionProspecto
from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.usuario.usuario import Usuario


class DictRowProspectoAdapter:

    def __init__(self, row: DictRow):
        self.row = row

    def to_prospecto(self) -> Prospecto:
        id = self.row['id_prospecto']
        id_cliente = self.row['id_cliente']
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
        rut_ej_evaluacion_asignado = self.row['rut_ej_evaluacion_asignado']
        nombre_ej_evaluacion_asignado = self.row['nombre_ej_evaluacion_asignado']
        id_linea_negocio = self.row['id_linea_negocio']  
        region = self.row['region']  
        comuna = self.row['comuna']  
        informacion_completa = self.row['informacion_completa']  
        prospecto_updated_at = self.row['prospecto_updated_at']

        id_company_planificacion = self.row['id_company_planificacion']
        nombre_company_planificacion = self.row['nombre_company_planificacion']
        prima_vigente_planificacion = self.row['prima_vigente_planificacion']
        termino_vigencia_planificacion = self.row['termino_vigencia_planificacion']
        monto_asegurado_vigente_planificacion = self.row['monto_asegurado_vigente_planificacion']
        fecha_envio_cotizacion_planificacion = self.row['fecha_envio_cotizacion_planificacion']

        planificacion = None

        if id_company_planificacion:

            company_poliza_vigente = CompanySeguros(
                id=id_company_planificacion,
                nombre=nombre_company_planificacion,
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

        ejecutivo_evaluacion = None

        if rut_ej_evaluacion_asignado is not None:
            ejecutivo_evaluacion = Usuario(
                rut = rut_ej_evaluacion_asignado,
                nombre = nombre_ej_evaluacion_asignado
            ) 

        return Prospecto(
            id = id,
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
            ejecutivo_evaluacion_asignado=ejecutivo_evaluacion,
            planificacion_prospecto=planificacion,
            ultima_actualizacion=prospecto_updated_at,
            informacion_completa=informacion_completa
        )