from pydantic import BaseModel


class GuardarValorUfRegionRequest(BaseModel):
    id: int | None = None
    region: str
    valor_uf_m2: float
