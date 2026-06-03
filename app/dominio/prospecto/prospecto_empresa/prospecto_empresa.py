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
        nombre_riesgo: str, 
        telefono_contacto: str, 
        correo_contacto: str | None, 
        direccion: str,
        region: str, 
        comuna: str, 
        observaciones: str | None, 
        linea_negocio: LineaNegocio, 
        registrado_por: Usuario, 
        companies_sugeridas: list[CompanySeguros],
        nombre_contacto: str,
        actividad: str,
        proceso_comercial: ProcesoComercial,
        ma_rc: float | None,
        ma_edificio: float | None,
        cantidad_trabajadores: int | None,
        ultima_actualizacion: datetime,
        id: int | None = None, 
        planificacion_prospecto: PlanificacionProspecto | None = None
    ):
        super().__init__(
            id=id,
            rut_riesgo=rut_riesgo,
            nombre_riesgo=nombre_riesgo,
            nombre_contacto=nombre_contacto,
            telefono_contacto=telefono_contacto,
            correo_contacto=correo_contacto,
            direccion=direccion,
            region=region,
            comuna=comuna,
            observaciones=observaciones,
            linea_negocio=linea_negocio,
            registrado_por=registrado_por,
            companies_sugeridas=companies_sugeridas,
            planificacion_prospecto=planificacion_prospecto,
            proceso_comercial=proceso_comercial,
            ultima_actualizacion=ultima_actualizacion
        )

        self.actividad = actividad
        self.ma_rc = ma_rc
        self.ma_edificio = ma_edificio
        self.cantidad_trabajadores = cantidad_trabajadores
        
        