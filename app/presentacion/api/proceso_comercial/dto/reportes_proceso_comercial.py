from pydantic import BaseModel

from app.presentacion.api.proceso_comercial.dto.estado_semaforo import EstadoSemaforo
from app.presentacion.api.proceso_comercial.dto.proceso_comercial_json import ProcesoComercialJson


class ReportesProcesoComercialDTO(BaseModel):
    proceso: ProcesoComercialJson
    fecha_ingreso_etapa: str
    dias_transcurridos: int
    porentaje_sla_consumido: float
    estado_semaforo: EstadoSemaforo
    dias_restantes: int
    dias_atraso: int
    mensaje_semaforo: str