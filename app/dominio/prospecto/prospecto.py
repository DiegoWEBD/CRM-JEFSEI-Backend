from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.comuna.comuna import Comuna
from app.dominio.estados.estado_particular.estado_particular import EstadoParticular
from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo
from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.usuario.usuario import Usuario
from datetime import datetime

class Prospecto:
    def __init__(
        self, 
        rut_riesgo: str | None, 
        nombre_riesgo: str, 
        telefono_contacto: str, 
        correo_contacto: str | None, 
        direccion: str, 
        comuna: Comuna, 
        estado: EstadoParticular, 
        observaciones: str | None, 
        linea_negocio: LineaNegocio, 
        registrado_por: Usuario, 
        companies_sugeridas: list[CompanySeguros], 
        fecha_registro: datetime | None = None,
        id: int | None = None,
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
        self.registrado_por = registrado_por
        self.companies_sugeridas = companies_sugeridas
        self.evaluacion_riesgo = evaluacion_riesgo
        self.id = id
        self.fecha_registro = fecha_registro