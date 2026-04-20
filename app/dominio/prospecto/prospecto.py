from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.estados.estado_particular.estado_particular import EstadoParticular
from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo
from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.usuario.usuario import Usuario

class Prospecto:
    def __init__(
        self, 
        rut_riesgo: str, 
        nombre_riesgo: str, 
        telefono_contacto: str, 
        correo_contacto: str, 
        direccion: str, 
        comuna: str, 
        estado: EstadoParticular, 
        observaciones: str, 
        linea_negocio: LineaNegocio, 
        asistente_comercial: Usuario, 
        companies_sugeridas: list[CompanySeguros], 
        evaluacion_riesgo: EvaluacionRiesgo | None = None
    ):
        self.rut_riesgo = rut_riesgo
        self.nombre_riesgo = nombre_riesgo
        self.telefono_contacto = telefono_contacto
        self.correo_contacto = correo_contacto
        self.direccion = direccion
        self.comuna = comuna
        self.estado = estado
        self.observaciones = observaciones
        self.linea_negocio = linea_negocio
        self.asistente_comercial = asistente_comercial
        self.companies_sugeridas = companies_sugeridas
        self.evaluacion_riesgo = evaluacion_riesgo