from pydantic import BaseModel


class AsignarEjecutivoComercialRequest(BaseModel):
    rut_ej_comercial: str