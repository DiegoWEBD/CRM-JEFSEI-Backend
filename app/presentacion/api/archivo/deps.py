from app.aplicacion.archivo.use_cases.eliminar_archivo import EliminarArchivoUseCase
from app.aplicacion.archivo.use_cases.obtener_archivo_por_id import ObtenerArchivoPorIdUseCase
from app.aplicacion.archivo.use_cases.obtener_archivos_prospecto import ObtenerArchivosProspectoUseCase
from app.aplicacion.archivo.use_cases.subir_archivo import SubirArchivoUseCase
from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.infraestructura.archivo.repositorio_archivos_postgres import RepositorioArchivosPostgres
from app.infraestructura.authorization.authorization_repository_postgres import AuthorizationRepositoryPostgres
from app.infraestructura.prospecto.repositorio_prospectos_postgres import RepositorioProspectosPostgres


def get_subir_archivo_use_case():
    return SubirArchivoUseCase(
        repositorio_archivos=RepositorioArchivosPostgres(),
        repositorio_prospectos=RepositorioProspectosPostgres(),
        authorization_service=AuthorizationService(AuthorizationRepositoryPostgres()),
    )


def get_obtener_archivos_prospecto_use_case():
    return ObtenerArchivosProspectoUseCase(
        repositorio_archivos=RepositorioArchivosPostgres(),
        repositorio_prospectos=RepositorioProspectosPostgres(),
        authorization_service=AuthorizationService(AuthorizationRepositoryPostgres()),
    )


def get_obtener_archivo_por_id_use_case():
    return ObtenerArchivoPorIdUseCase(
        repositorio_archivos=RepositorioArchivosPostgres(),
        repositorio_prospectos=RepositorioProspectosPostgres(),
        authorization_service=AuthorizationService(AuthorizationRepositoryPostgres()),
    )


def get_eliminar_archivo_use_case():
    return EliminarArchivoUseCase(
        repositorio_archivos=RepositorioArchivosPostgres(),
        repositorio_prospectos=RepositorioProspectosPostgres(),
        authorization_service=AuthorizationService(AuthorizationRepositoryPostgres()),
    )
