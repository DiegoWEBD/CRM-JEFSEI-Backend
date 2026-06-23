from pydantic import BaseModel

from app.presentacion.api.historial_estado.dto.historial_estado_resumen import HistorialEstadoResumen


class HistorialEtapaResumen(BaseModel):
    etapa: str
    fecha_entrada_etapa: str
    estados: list[HistorialEstadoResumen]