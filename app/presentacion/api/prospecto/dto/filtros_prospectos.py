from typing import Optional

from pydantic import BaseModel


class FiltrosProspectos(BaseModel):
    filtro: Optional[str] = None
    texto_busqueda: Optional[str] = None
    pagina: int = 1
    tamano_pagina: int = 25
