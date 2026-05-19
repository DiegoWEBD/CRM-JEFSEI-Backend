from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.comuna.comuna import Comuna
from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo
from app.dominio.historial_estado.historial_estado import HistorialEstado
from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.planificacion_prospecto.planificacion_prospecto import PlanificacionProspecto
from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.solicitud_evaluacion_riesgo.solicitud_evaluacion_riesgo import SolicitudEvaluacionRiesgo
from app.dominio.usuario.usuario import Usuario

class ProspectoCondominio(Prospecto):
    def __init__(
        self,
        rut_riesgo: str | None, 
        nombre_riesgo: str, 
        nombre_contacto: str,
        telefono_contacto: str, 
        correo_contacto: str | None, 
        direccion: str, 
        comuna: Comuna, 
        observaciones: str | None, 
        linea_negocio: LineaNegocio, 
        registrado_por: Usuario, 
        ejecutivo_comercial_asignado: Usuario | None,
        ejecutivo_evaluacion_asignado: Usuario | None,
        companies_sugeridas: list[CompanySeguros],   
        historial_estados: list[HistorialEstado], 
        cargo_contacto: str | None, 
        id: int | None = None, 
        planificacion_prospecto: PlanificacionProspecto | None = None,
        evaluacion_riesgo: EvaluacionRiesgo | None = None,
        solicitud_evaluacion_riesgo: SolicitudEvaluacionRiesgo | None = None,
        tiene_locales_comerciales: bool | None = None,
        uso_del_condominio: str | None = None,
        numero_pisos: int | None = None,
        numero_torres: int | None = None,
        cantidad_departamentos: int | None = None,
        cantidad_subterraneos: int | None = None,
        tiene_piscina: bool | None = None,
        year_construccion: int | None = None,
        metros_cuadrados: float | None = None,
        desea_ser_contactado: bool | None = None
    ):
        super().__init__(
            id=id,
            rut_riesgo=rut_riesgo,
            nombre_riesgo=nombre_riesgo,
            nombre_contacto=nombre_contacto,
            telefono_contacto=telefono_contacto,
            correo_contacto=correo_contacto,
            direccion=direccion,
            comuna=comuna,
            observaciones=observaciones,
            linea_negocio=linea_negocio,
            registrado_por=registrado_por,
            companies_sugeridas=companies_sugeridas,
            historial_estados=historial_estados,
            solicitud_evaluacion_riesgo=solicitud_evaluacion_riesgo,
            evaluacion_riesgo=evaluacion_riesgo,
            planificacion_prospecto=planificacion_prospecto,
            ejecutivo_comercial_asignado=ejecutivo_comercial_asignado,
            ejecutivo_evaluacion_asignado=ejecutivo_evaluacion_asignado
        )
        
        self.tiene_locales_comerciales = tiene_locales_comerciales
        self.uso_del_condominio = uso_del_condominio
        self.numero_pisos = numero_pisos
        self.numero_torres = numero_torres
        self.cantidad_departamentos = cantidad_departamentos
        self.cantidad_subterraneos = cantidad_subterraneos
        self.tiene_piscina = tiene_piscina
        self.year_construccion = year_construccion
        self.cargo_contacto = cargo_contacto
        self.metros_cuadrados = metros_cuadrados
        self.desea_ser_contactado = desea_ser_contactado