from pydantic import BaseModel


class ArmarEstudioComercialRequest(BaseModel):
    id_prospecto: int
    infraseguro_primer_ejemplo: float
    infraseguro_segundo_ejemplo: float
    cantidad_cuotas: int