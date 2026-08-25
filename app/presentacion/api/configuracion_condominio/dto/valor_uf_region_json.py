from pydantic import BaseModel


class ValorUfRegionJson(BaseModel):
    id: int | None
    region: str
    valor_uf_m2: float
