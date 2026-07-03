from pydantic import BaseModel

from app.presentacion.api.linea_negocio.dto.linea_negocio_json import LineaNegocioJson
from app.presentacion.api.planificacion_prospecto.dto.planificacion_prospecto_json import PlanificacionProspectoJson
from app.presentacion.api.usuario.dto.usuario_json_resumen import UsuarioJsonResumen


class ProspectoJson(BaseModel):
    id: int
    id_cliente: int | None
    rut_riesgo: str | None 
    nombre_riesgo: str | None
    telefono_contacto: str | None 
    correo_contacto: str | None 
    direccion: str | None 
    region: str | None
    comuna: str | None 
    observaciones: str | None 
    linea_negocio: LineaNegocioJson 
    registrado_por: UsuarioJsonResumen 
    ejecutivo_comercial_asignado: UsuarioJsonResumen | None
    ejecutivo_evaluacion_asignado: UsuarioJsonResumen | None
    ultima_actualizacion: str
    informacion_completa: bool
    planificacion_prospecto: PlanificacionProspectoJson | None