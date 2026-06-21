from fastapi import Query

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.proceso_comercial.use_cases.cerrar_proceso_comercial import CerrarProcesoComercialUseCase
from app.aplicacion.proceso_comercial.use_cases.crear_proceso_comercial import CrearProcesoComercialUseCase
from app.aplicacion.proceso_comercial.use_cases.obtener_todos_procesos_comerciales import ObtenerTodosProcesosComercialesUseCase
from app.infraestructura.authorization.authorization_repository_postgres import AuthorizationRepositoryPostgres
from app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres import RepositorioProcesosComercialesPostgres
from app.infraestructura.prospecto.repositorio_prospectos_postgres import RepositorioProspectosPostgres
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

def get_cerrar_proceso_comercial_use_case():
    repositorio = RepositorioProcesosComercialesPostgres()
    return CerrarProcesoComercialUseCase(repositorio)

def get_crear_proceso_comercial_use_case():
    authorization_repository = AuthorizationRepositoryPostgres()
    authorization_service = AuthorizationService(authorization_repository)
    repositorio_prospectos = RepositorioProspectosPostgres()
    repositorio_procesos = RepositorioProcesosComercialesPostgres()

    return CrearProcesoComercialUseCase(
        authorization_service=authorization_service,
        repositorio_procesos_comerciales=repositorio_procesos,
        repositorio_prospectos=repositorio_prospectos
    )