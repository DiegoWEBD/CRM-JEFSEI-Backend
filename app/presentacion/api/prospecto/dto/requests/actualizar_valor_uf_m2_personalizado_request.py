from pydantic import BaseModel


class ActualizarValorUfM2PersonalizadoRequest(BaseModel):
    valor_uf_m2_personalizado: float | None
