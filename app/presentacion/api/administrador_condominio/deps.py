from fastapi import Query

from app.aplicacion.administrador_condominio.use_cases.obtener_administrador_por_id import (
    ObtenerAdministradorPorIdUseCase,
)

from app.aplicacion.administrador_condominio.use_cases.registrar_administrador import (
    RegistrarAdministradorUseCase,
)
from app.aplicacion.administrador_condominio.use_cases.actualizar_administrador import (
    ActualizarAdministradorUseCase,
)
from app.aplicacion.administrador_condominio.servicios.consulta_administradores_service import (
    ConsultaAdministradoresService,
)
from app.aplicacion.prospecto.servicios.consulta_prospectos_service import (
    ConsultaProspectosService,
)
from app.infraestructura.administrador_condominio.repositorio_administradores_postgres import (
    RepositorioAdministradoresPostgres,
)
from app.infraestructura.administrador_condominio.servicios.consulta_administradores_postgres_service import (
    ConsultaAdministradoresPostgresService,
)
from app.infraestructura.prospecto.servicios.consulta_prospectos_postgres_service import (
    ConsultaProspectosPostgresService,
)
from app.presentacion.api.administrador_condominio.dto.filtros_administradores import (
    FiltrosAdministradores,
)


def get_obtener_administrador_por_id_use_case() -> ObtenerAdministradorPorIdUseCase:
    repositorio = RepositorioAdministradoresPostgres()
    return ObtenerAdministradorPorIdUseCase(repositorio)


def get_registrar_administrador_use_case() -> RegistrarAdministradorUseCase:
    repositorio = RepositorioAdministradoresPostgres()
    return RegistrarAdministradorUseCase(repositorio)


def get_actualizar_administrador_use_case() -> ActualizarAdministradorUseCase:
    repositorio = RepositorioAdministradoresPostgres()
    return ActualizarAdministradorUseCase(repositorio)


def get_filtros_administradores(
    pagina: int = Query(1, ge=1),
    tamano_pagina: int = Query(25, ge=1, le=100),
    texto_busqueda: str | None = Query(None),
) -> FiltrosAdministradores:
    return FiltrosAdministradores(
        pagina=pagina,
        tamano_pagina=tamano_pagina,
        texto_busqueda=texto_busqueda,
    )


def get_consulta_administradores_service() -> ConsultaAdministradoresService:
    return ConsultaAdministradoresPostgresService()


def get_consulta_prospectos_service() -> ConsultaProspectosService:
    return ConsultaProspectosPostgresService()
