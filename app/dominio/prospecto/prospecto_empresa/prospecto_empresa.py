from datetime import datetime

from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.planificacion_prospecto.planificacion_prospecto import PlanificacionProspecto
from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial
from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.usuario.usuario import Usuario

class ProspectoEmpresa(Prospecto):
    def __init__(
        self,
        rut_riesgo: str | None, 
        nombre_riesgo: str | None, 
        telefono_contacto: str | None, 
        correo_contacto: str | None, 
        direccion: str | None,
        region: str | None, 
        comuna: str | None, 
        observaciones: str | None, 
        linea_negocio: LineaNegocio, 
        registrado_por: Usuario, 
        companies_sugeridas: list[CompanySeguros],
        nombre_contacto: str,
        actividad: str,
        proceso_comercial: ProcesoComercial,
        informacion_completa: bool,
        ma_rc: float | None,
        ma_edificio: float | None,
        cantidad_trabajadores: int | None,
        ultima_actualizacion: datetime,
        id: int | None = None, 
        id_cliente: int | None = None,
        planificacion_prospecto: PlanificacionProspecto | None = None,
        ejecutivo_comercial_asignado: Usuario | None = None,
        ejecutivo_evaluacion_asignado: Usuario | None = None,
        ejecutivo_cobranza_asignado: Usuario | None = None,
        ejecutivo_renovacion_asignado: Usuario | None = None,
    ):
        super().__init__(
            id=id,
            id_cliente=id_cliente,
            rut_riesgo=rut_riesgo,
            nombre_riesgo=nombre_riesgo,
            telefono_contacto=telefono_contacto,
            correo_contacto=correo_contacto,
            direccion=direccion,
            region=region,
            comuna=comuna,
            observaciones=observaciones,
            linea_negocio=linea_negocio,
            registrado_por=registrado_por,
            ejecutivo_comercial_asignado=ejecutivo_comercial_asignado,
            ejecutivo_evaluacion_asignado=ejecutivo_evaluacion_asignado,
            ejecutivo_cobranza_asignado=ejecutivo_cobranza_asignado,
            ejecutivo_renovacion_asignado=ejecutivo_renovacion_asignado,
            planificacion_prospecto=planificacion_prospecto,
            ultima_actualizacion=ultima_actualizacion,
            informacion_completa=informacion_completa
        )

        self.actividad = actividad
        self.ma_rc = ma_rc
        self.ma_edificio = ma_edificio
        self.cantidad_trabajadores = cantidad_trabajadores
        
        