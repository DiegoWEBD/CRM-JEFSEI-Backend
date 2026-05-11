from pydantic import BaseModel

from app.presentacion.api.historial_estado.dto.historial_estado_json import HistorialEstadoJson
from app.presentacion.api.usuario.dto.usuario_json_resumen import UsuarioJsonResumen


class ProspectoJson(BaseModel):
    rut_riesgo: str | None 
    nombre_riesgo: str 
    nombre_contacto: str
    telefono_contacto: str 
    correo_contacto: str | None 
    direccion: str 
    comuna: str 
    historial_estados: list[HistorialEstadoJson] 
    observaciones: str | None 
    linea_negocio: str 
    registrado_por: UsuarioJsonResumen 
    companies_sugeridas: list[str]
    id: int | None = None