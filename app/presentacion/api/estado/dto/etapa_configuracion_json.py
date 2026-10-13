from pydantic import BaseModel

from app.presentacion.api.estado.dto.estado_configuracion_json import EstadoConfiguracionJson


class EtapaConfiguracionJson(BaseModel):
    codigo_etapa: str
    nombre_etapa: str
    dias_limite_etapa: int | None
    estados: list[EstadoConfiguracionJson]
