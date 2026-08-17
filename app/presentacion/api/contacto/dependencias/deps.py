from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.contacto.use_cases.actualizar_contacto import ActualizarContactoUseCase
from app.aplicacion.contacto.use_cases.eliminar_contacto import EliminarContactoUseCase
from app.aplicacion.contacto.use_cases.obtener_contactos_prospecto import ObtenerContactosProspectoUseCase
from app.aplicacion.contacto.use_cases.registrar_contacto import RegistrarContactoUseCase
from app.infraestructura.authorization.authorization_repository_postgres import AuthorizationRepositoryPostgres
from app.infraestructura.contacto.repositorio_contactos_postgres import RepositorioContactosPostgres
from app.infraestructura.prospecto.repositorio_prospectos_postgres import RepositorioProspectosPostgres


def get_obtener_contactos_prospecto_use_case() -> ObtenerContactosProspectoUseCase:
    repositorio_contactos = RepositorioContactosPostgres()
    repositorio_prospectos = RepositorioProspectosPostgres()
    authorization_service = AuthorizationService(AuthorizationRepositoryPostgres())
    return ObtenerContactosProspectoUseCase(
        repositorio_contactos=repositorio_contactos,
        repositorio_prospectos=repositorio_prospectos,
        authorization_service=authorization_service,
    )


def get_registrar_contacto_use_case() -> RegistrarContactoUseCase:
    repositorio_contactos = RepositorioContactosPostgres()
    repositorio_prospectos = RepositorioProspectosPostgres()
    authorization_service = AuthorizationService(AuthorizationRepositoryPostgres())
    return RegistrarContactoUseCase(
        repositorio_contactos=repositorio_contactos,
        repositorio_prospectos=repositorio_prospectos,
        authorization_service=authorization_service,
    )


def get_actualizar_contacto_use_case() -> ActualizarContactoUseCase:
    repositorio_contactos = RepositorioContactosPostgres()
    authorization_service = AuthorizationService(AuthorizationRepositoryPostgres())
    return ActualizarContactoUseCase(
        repositorio_contactos=repositorio_contactos,
        authorization_service=authorization_service,
    )


def get_eliminar_contacto_use_case() -> EliminarContactoUseCase:
    repositorio_contactos = RepositorioContactosPostgres()
    authorization_service = AuthorizationService(AuthorizationRepositoryPostgres())
    return EliminarContactoUseCase(
        repositorio_contactos=repositorio_contactos,
        authorization_service=authorization_service,
    )