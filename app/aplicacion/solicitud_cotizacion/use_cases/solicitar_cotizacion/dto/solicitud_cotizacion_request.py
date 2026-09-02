from typing import Optional

from pydantic import BaseModel

from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.dto.solicitud_cotizacion_accidentes_personales_request.actividad_accidentes_personales_request import ActividadAccidentesPersonalesRequest


class SolicitudCotizacionRequest(BaseModel):
    prioridad: str
    observaciones: str | None
    tipo: str
    motivo_recotizacion: Optional[str] = None
    id_solicitud_previa: int | None
    numero_guardias: int | None = None
    monto_asegurado_total: float | None = None
    nombre_excel: str | None = None
    actividades: list[ActividadAccidentesPersonalesRequest] | None = None
    actividad_del_condominio: str | None = None
    limite: float | None = None
