from fastapi import Depends

from app.aplicacion.auditoria.audit_service import AuditService
from app.aplicacion.auth.use_cases.cerrar_sesion import CerrarSesionUseCase
from app.aplicacion.auth.use_cases.rotar_sesion import RotarSesionUseCase
from app.infraestructura.auditoria.repositorio_auditoria_postgres import RepositorioAuditoriaPostgres
from app.infraestructura.auditoria.repositorio_sesiones_postgres import RepositorioSesionesPostgres
from app.infraestructura.auth.jwt_authentication_service import JwtAuthenticationService
from app.infraestructura.usuario.repositorio_usuarios_postgres import RepositorioUsuariosPostgres


def get_audit_service() -> AuditService:
    """Se construye por request: el repositorio abre conexiones por llamada."""
    return AuditService(RepositorioAuditoriaPostgres())


def get_repositorio_sesiones() -> RepositorioSesionesPostgres:
    return RepositorioSesionesPostgres()


def get_rotar_sesion_use_case(
    repositorio_sesiones: RepositorioSesionesPostgres = Depends(get_repositorio_sesiones),
    audit_service: AuditService = Depends(get_audit_service),
) -> RotarSesionUseCase:
    # JwtAuthenticationService es sin estado, se puede compartir.
    return RotarSesionUseCase(
        repositorio_sesiones=repositorio_sesiones,
        repositorio_usuarios=RepositorioUsuariosPostgres(),
        authentication_service=JwtAuthenticationService(),
        audit_service=audit_service,
    )


def get_cerrar_sesion_use_case(
    repositorio_sesiones: RepositorioSesionesPostgres = Depends(get_repositorio_sesiones),
    audit_service: AuditService = Depends(get_audit_service),
) -> CerrarSesionUseCase:
    return CerrarSesionUseCase(
        repositorio_sesiones=repositorio_sesiones,
        audit_service=audit_service,
    )
