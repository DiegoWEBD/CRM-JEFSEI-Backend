from pydantic import BaseModel

from app.presentacion.api.estado_informativo.dto.estado_informativo_json import EstadoInformativoJson
from app.presentacion.api.usuario.dto.usuario_json import UsuarioJson


class HistorialEstadoJson(BaseModel):
    estado: EstadoInformativoJson
    fecha_registro: str
    observacion: str | None
    registrado_por: UsuarioJson
    dias_transcurridos: int
