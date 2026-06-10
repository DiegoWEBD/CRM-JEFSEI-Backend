from datetime import datetime

from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.planificacion_prospecto.planificacion_prospecto import PlanificacionProspecto
from app.dominio.usuario.usuario import Usuario

class Prospecto:
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
        ejecutivo_comercial_asignado: Usuario | None,
        #companies_sugeridas: list[CompanySeguros],
        #proceso_comercial: ProcesoComercial,
        ultima_actualizacion: datetime = datetime.now(),
        planificacion_prospecto: PlanificacionProspecto | None = None,
        id: int | None = None,
        id_cliente: int | None = None
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
        self.ejecutivo_comercial_asignado = ejecutivo_comercial_asignado
        self.id = id
        self.id_cliente = id_cliente
        self.planificacion_prospecto = planificacion_prospecto
        self.ultima_actualizacion = ultima_actualizacion