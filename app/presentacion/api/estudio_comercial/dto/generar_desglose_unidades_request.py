from pydantic import BaseModel


class GenerarDesgloseUnidadesRequest(BaseModel):
    id_solicitud: int
    ids_cotizacion: list[int]
