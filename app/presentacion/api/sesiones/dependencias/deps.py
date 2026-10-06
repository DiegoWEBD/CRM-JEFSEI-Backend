from app.aplicacion.auditoria.servicio_auditoria import ServicioAuditoria
from app.aplicacion.auth.use_cases.obtener_sesiones import ObtenerSesionesUseCase
from app.aplicacion.auth.use_cases.revocar_sesion_admin import RevocarSesionAdminUseCase
from app.aplicacion.auth.use_cases.revocar_todas_sesiones_usuario_admin import (
    RevocarTodasSesionesUsuarioAdminUseCase,
)
from app.infraestructura.auditoria.repositorio_auditoria_postgres import RepositorioAuditoriaPostgres
from app.infraestructura.auth.repositorio_sesiones_postgres import RepositorioSesionesPostgres


def get_servicio_auditoria() -> ServicioAuditoria:
    return ServicioAuditoria(RepositorioAuditoriaPostgres())


def get_obtener_sesiones_use_case() -> ObtenerSesionesUseCase:
    return ObtenerSesionesUseCase(RepositorioSesionesPostgres())


def get_revocar_sesion_admin_use_case() -> RevocarSesionAdminUseCase:
    return RevocarSesionAdminUseCase(
        RepositorioSesionesPostgres(), get_servicio_auditoria()
    )


def get_revocar_todas_sesiones_usuario_admin_use_case() -> RevocarTodasSesionesUsuarioAdminUseCase:
    return RevocarTodasSesionesUsuarioAdminUseCase(
        RepositorioSesionesPostgres(), get_servicio_auditoria()
    )