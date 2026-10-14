from typing import Union

from pydantic import BaseModel

from app.presentacion.api.proceso_comercial.dto.estado_semaforo import EstadoSemaforo
from app.presentacion.api.proceso_comercial.dto.proceso_comercial_json import ProcesoComercialJson
from app.presentacion.api.proceso_comercial.dto.reportes_proceso_comercial_cerrado import ReportesProcesoComercialCerradoDTO


class ReportesProcesoComercialDTO(BaseModel):
    proceso: ProcesoComercialJson
    fecha_ingreso_estado: str | None
    dias_transcurridos: int | None
    porentaje_sla_consumido: float | None
    estado_semaforo: EstadoSemaforo
    dias_limite: int | None
    dias_restantes: int | None
    dias_atraso: int | None
    mensaje_semaforo: str | None


class ReportesProcesosComercialesResponse(BaseModel):
    data: list[Union[ReportesProcesoComercialDTO, ReportesProcesoComercialCerradoDTO]]
    total: int
    pagina: int
    tamano_pagina: int
    total_paginas: int
    contadores_estado: dict