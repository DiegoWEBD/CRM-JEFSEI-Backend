from typing import Union

from pydantic import BaseModel

from app.presentacion.api.proceso_comercial.dto.estado_semaforo import EstadoSemaforo
from app.presentacion.api.proceso_comercial.dto.proceso_comercial_json import ProcesoComercialJson
from app.presentacion.api.proceso_comercial.dto.reportes_proceso_comercial_cerrado import ReportesProcesoComercialCerradoDTO


class ReportesProcesoComercialDTO(BaseModel):
    proceso: ProcesoComercialJson
    fecha_ingreso_estado: str | None
    # Días decimales (fracción de día con precisión de horas, 24/7).
    dias_transcurridos: float | None
    porentaje_sla_consumido: float | None
    estado_semaforo: EstadoSemaforo
    dias_limite: int | None
    dias_restantes: float | None
    dias_atraso: float | None
    mensaje_semaforo: str | None


class ReportesProcesosComercialesResponse(BaseModel):
    data: list[Union[ReportesProcesoComercialDTO, ReportesProcesoComercialCerradoDTO]]
    total: int
    pagina: int
    tamano_pagina: int
    total_paginas: int
    contadores_estado: dict