from typing import Union

from pydantic import BaseModel

from app.presentacion.api.proceso_comercial.dto.estado_semaforo import EstadoSemaforo
from app.presentacion.api.proceso_comercial.dto.proceso_comercial_json import ProcesoComercialJson
from app.presentacion.api.proceso_comercial.dto.reportes_proceso_comercial_cerrado import ReportesProcesoComercialCerradoDTO


class ReportesProcesoComercialDTO(BaseModel):
    proceso: ProcesoComercialJson
    fecha_ingreso_etapa: str
    dias_transcurridos: int
    porentaje_sla_consumido: float
    estado_semaforo: EstadoSemaforo
    dias_restantes: int
    dias_atraso: int
    mensaje_semaforo: str


class ReportesProcesosComercialesResponse(BaseModel):
    data: list[Union[ReportesProcesoComercialDTO, ReportesProcesoComercialCerradoDTO]]
    total: int
    pagina: int
    tamano_pagina: int
    total_paginas: int
    contadores_estado: dict