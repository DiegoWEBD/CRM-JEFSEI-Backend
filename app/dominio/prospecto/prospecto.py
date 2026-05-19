from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.comuna.comuna import Comuna
from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo
from app.dominio.historial_estado.historial_estado import HistorialEstado
from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.planificacion_prospecto.planificacion_prospecto import PlanificacionProspecto
from app.dominio.solicitud_evaluacion_riesgo.solicitud_evaluacion_riesgo import SolicitudEvaluacionRiesgo
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
        comuna: Comuna, 
        historial_estados: list[HistorialEstado], 
        observaciones: str | None, 
        linea_negocio: LineaNegocio, 
        registrado_por: Usuario, 
        ejecutivo_comercial_asignado: Usuario | None,
        ejecutivo_evaluacion_asignado: Usuario | None,
        companies_sugeridas: list[CompanySeguros],
        planificacion_prospecto: PlanificacionProspecto | None = None,
        id: int | None = None,
        evaluacion_riesgo: EvaluacionRiesgo | None = None,
        solicitud_evaluacion_riesgo: SolicitudEvaluacionRiesgo | None = None
    ):
        self.rut_riesgo = rut_riesgo
        self.nombre_riesgo = nombre_riesgo
        self.telefono_contacto = telefono_contacto
        self.correo_contacto = correo_contacto
        self.direccion = direccion
        self.comuna = comuna
        self.historial_estados = historial_estados
        self.observaciones = observaciones
        self.linea_negocio = linea_negocio
        self.registrado_por = registrado_por
        self.companies_sugeridas = companies_sugeridas
        self.evaluacion_riesgo = evaluacion_riesgo
        self.id = id
        self.nombre_contacto = nombre_contacto
        self.planificacion_prospecto = planificacion_prospecto
        self.solicitud_evaluacion_riesgo = solicitud_evaluacion_riesgo
        self.ejecutivo_comercial_asignado = ejecutivo_comercial_asignado
        self.ejecutivo_evaluacion_asignado = ejecutivo_evaluacion_asignado