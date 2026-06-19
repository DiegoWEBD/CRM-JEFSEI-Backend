from pydantic import BaseModel

from app.presentacion.api.estado_informativo.dto.estado_informativo_json import EstadoInformativoJson
from app.presentacion.api.etapa_proceso_comercial.dto.etapa_proceso_comercial_json import EtapaProcesoComercialJson
from app.presentacion.api.usuario.dto.usuario_json_resumen import UsuarioJsonResumen


class ProcesoComercialJson(BaseModel):
    id: int
    ejecutivo_comercial: UsuarioJsonResumen | None
    ejecutivo_evaluacion: UsuarioJsonResumen | None
    id_prospecto: int
    nombre_cliente: str
    producto: str
    estado_actual: EstadoInformativoJson
    etapa_actual: EtapaProcesoComercialJson
    cerrado: bool