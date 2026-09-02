from fastapi import Query

from app.presentacion.api.dto.paginacion_params import PaginacionParams


def get_paginacion_params(
    pagina: int = Query(1, ge=1),
    tamano_pagina: int = Query(15, ge=1, le=100),
    texto_busqueda: str | None = Query(None),
) -> PaginacionParams:
    return PaginacionParams(pagina=pagina, tamano_pagina=tamano_pagina, texto_busqueda=texto_busqueda)
