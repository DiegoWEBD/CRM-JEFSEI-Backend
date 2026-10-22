from pydantic import BaseModel

from app.presentacion.api.etapa_proceso_comercial.dto.etapa_proceso_comercial_json import EtapaProcesoComercialJson


class EstadoInformativoJson(BaseModel):
    codigo: str 
    nombre: str
    etapa: EtapaProcesoComercialJson
