from pydantic import BaseModel

from app.presentacion.api.estado.dto.estado_configuracion_json import EstadoConfiguracionJson


class EtapaConfiguracionJson(BaseModel):
    codigo_etapa: str
    nombre_etapa: str
    estados: list[EstadoConfiguracionJson]
