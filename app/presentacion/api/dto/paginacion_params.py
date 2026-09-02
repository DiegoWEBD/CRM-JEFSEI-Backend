from pydantic import BaseModel


class PaginacionParams(BaseModel):
    pagina: int = 1
    tamano_pagina: int = 15
    texto_busqueda: str | None = None
