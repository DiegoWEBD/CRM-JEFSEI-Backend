from datetime import datetime

from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.planificacion_prospecto.planificacion_prospecto import PlanificacionProspecto
from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial
from app.dominio.usuario.usuario import Usuario

class Prospecto:
    def __init__(
        self, 
        rut_riesgo: str | None, 
        nombre_riesgo: str, 
        nombre_contacto: str,
        telefono_contacto: str, 
        correo_contacto: str | None, 
        direccion: str, 
        region: str,
        comuna: str,    
        observaciones: str | None, 
        linea_negocio: LineaNegocio, 
        registrado_por: Usuario, 
        companies_sugeridas: list[CompanySeguros],
        proceso_comercial: ProcesoComercial,
        ultima_actualizacion: datetime,
        planificacion_prospecto: PlanificacionProspecto | None = None,
        id: int | None = None
    ):
        self.rut_riesgo = rut_riesgo
        self.nombre_riesgo = nombre_riesgo
        self.telefono_contacto = telefono_contacto
        self.correo_contacto = correo_contacto
        self.direccion = direccion
        self.region = region
        self.comuna = comuna
        self.observaciones = observaciones
        self.linea_negocio = linea_negocio
        self.registrado_por = registrado_por
        self.companies_sugeridas = companies_sugeridas
        self.id = id
        self.nombre_contacto = nombre_contacto
        self.planificacion_prospecto = planificacion_prospecto
        self.proceso_comercial = proceso_comercial
        self.ultima_actualizacion = ultima_actualizacion