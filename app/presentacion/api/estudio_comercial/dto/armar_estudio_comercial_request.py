from pydantic import BaseModel

from app.presentacion.api.estudio_comercial.dto.seccion_estudio_comercial_request import SeccionEstudioComercialRequest


class ArmarEstudioComercialRequest(BaseModel):
    id_prospecto: int
    infraseguro_primer_ejemplo: float
    infraseguro_segundo_ejemplo: float
    cantidad_cuotas: int
    ids_cotizacion: list[int]
    valor_uf: float
    secciones: list[SeccionEstudioComercialRequest]