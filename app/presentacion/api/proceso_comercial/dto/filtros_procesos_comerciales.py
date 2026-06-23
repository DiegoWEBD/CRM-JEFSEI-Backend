from pydantic import BaseModel
from typing import Optional


class FiltrosProcesosComerciales(BaseModel):
    texto_busqueda: Optional[str] = None
    ejecutivos: Optional[list[str]] = None
    etapas: Optional[list[str]] = None
    estado_semaforo: Optional[list[str]] = None
    estado_proceso: Optional[str] = None
    cerrado: Optional[bool] = None
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None

    pagina: int = 1
    tamano_pagina: int = 25