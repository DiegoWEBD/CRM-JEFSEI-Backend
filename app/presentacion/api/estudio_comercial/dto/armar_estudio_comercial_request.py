from pydantic import BaseModel

from app.presentacion.api.estudio_comercial.dto.seccion_estudio_comercial_request import SeccionEstudioComercialRequest


class ArmarEstudioComercialRequest(BaseModel):
    id_prospecto: int
    monto_asegurado_actual: float | None
    con_monto_sugerido: bool
    infraseguro_primer_ejemplo: float | None
    infraseguro_segundo_ejemplo: float | None
    cantidad_cuotas: int
    ids_cotizacion: list[int]
    valor_uf: float
    secciones: list[SeccionEstudioComercialRequest] | None