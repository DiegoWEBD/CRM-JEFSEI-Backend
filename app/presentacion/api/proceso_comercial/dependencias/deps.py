from fastapi import Query

from app.aplicacion.proceso_comercial.use_cases.obtener_todos_procesos_comerciales import ObtenerTodosProcesosComercialesUseCase
from app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres import RepositorioProcesosComercialesPostgres
from app.presentacion.api.proceso_comercial.dto.filtros_procesos_comerciales import FiltrosProcesosComerciales


def get_obtener_todos_procesos_comerciales_use_case():
    repositorio = RepositorioProcesosComercialesPostgres()
    return ObtenerTodosProcesosComercialesUseCase(repositorio)


def get_filtros(
    texto_busqueda: str | None = Query(None),
    ejecutivos: list[str] | None = Query(None),
    etapas: list[str] | None = Query(None),
    estado_semaforo: list[str] | None = Query(None),
    estado_proceso: str | None = Query(None),
    fecha_desde: str | None = Query(None),
    fecha_hasta: str | None = Query(None),
    pagina: int = Query(1),
    tamano_pagina: int = Query(25),
) -> FiltrosProcesosComerciales:

    return FiltrosProcesosComerciales(
        texto_busqueda=texto_busqueda,
        ejecutivos=ejecutivos,
        etapas=etapas,
        estado_semaforo=estado_semaforo,
        estado_proceso=estado_proceso,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        pagina=pagina,
        tamano_pagina=tamano_pagina,
    )