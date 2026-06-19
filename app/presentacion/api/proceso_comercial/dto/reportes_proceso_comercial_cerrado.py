from pydantic import BaseModel

from app.presentacion.api.proceso_comercial.dto.estado_semaforo import EstadoSemaforo
from app.presentacion.api.proceso_comercial.dto.proceso_comercial_json import ProcesoComercialJson


class ReportesProcesoComercialCerradoDTO(BaseModel):
    proceso: ProcesoComercialJson
    estado_semaforo: EstadoSemaforo