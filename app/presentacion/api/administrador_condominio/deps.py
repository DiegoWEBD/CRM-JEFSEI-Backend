from app.aplicacion.administrador_condominio.use_cases.obtener_administrador_por_id import (
    ObtenerAdministradorPorIdUseCase,
)
from app.aplicacion.administrador_condominio.use_cases.obtener_administradores import (
    ObtenerAdministradoresUseCase,
)
from app.aplicacion.prospecto.servicios.consulta_prospectos_service import (
    ConsultaProspectosService,
)
from app.infraestructura.administrador_condominio.repositorio_administradores_postgres import (
    RepositorioAdministradoresPostgres,
)
from app.infraestructura.prospecto.servicios.consulta_prospectos_postgres_service import (
    ConsultaProspectosPostgresService,
)


def get_obtener_administradores_use_case() -> ObtenerAdministradoresUseCase:
    repositorio = RepositorioAdministradoresPostgres()
    return ObtenerAdministradoresUseCase(repositorio)


def get_obtener_administrador_por_id_use_case() -> ObtenerAdministradorPorIdUseCase:
    repositorio = RepositorioAdministradoresPostgres()
    return ObtenerAdministradorPorIdUseCase(repositorio)


def get_consulta_prospectos_service() -> ConsultaProspectosService:
    return ConsultaProspectosPostgresService()
