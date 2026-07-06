from pydantic import BaseModel


class AsignarEjecutivoCobranzaRequest(BaseModel):
    rut_ej_cobranza: str | None = None
