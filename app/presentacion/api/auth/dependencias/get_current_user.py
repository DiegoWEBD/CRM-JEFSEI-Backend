from fastapi import Depends, HTTPException, status, Request

from app.aplicacion.auth.authentication_service import AuthenticationService
from app.aplicacion.auditoria.audit_service import AuditService
from app.aplicacion.usuario.use_cases.obtener_usuario import ObtenerUsuarioUseCase
from app.dominio.usuario.usuario import Usuario
from app.infraestructura.auditoria.middleware_auditoria import CLAVE_ESTADO
from app.infraestructura.auth.jwt_authentication_service import JwtAuthenticationService
from app.infraestructura.auditoria.repositorio_sesiones_postgres import RepositorioSesionesPostgres
from app.presentacion.api.auth.dependencias.get_sesion_use_cases import get_audit_service
from app.presentacion.api.usuario.deps import get_obtener_usuario_use_case

NO_AUTENTICADO = "Usuario no autenticado"


def get_authentication_service() -> AuthenticationService:
    return JwtAuthenticationService()


def get_repositorio_sesiones_dep() -> RepositorioSesionesPostgres:
    return RepositorioSesionesPostgres()


def get_current_user(
    request: Request,
    authentication_service: AuthenticationService = Depends(get_authentication_service),
    use_case: ObtenerUsuarioUseCase = Depends(get_obtener_usuario_use_case),
    repositorio_sesiones: RepositorioSesionesPostgres = Depends(get_repositorio_sesiones_dep),
    audit_service: AuditService = Depends(get_audit_service),
) -> Usuario:
    """Valida el access token contra el estado real de la sesión.

    Antes el JWT bastaba por sí solo: un token no revocado seguía sirviendo
    hasta 15 minutos después de cerrar sesión. Ahora se exige que la sesión
    exista, no esté revocada y no haya vencido, y además se publica la
    identidad en el AuditContext para que los eventos posterioresecutivos
    queden atribuidos a esta sesión concreta.
    """
    token = request.cookies.get("token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=NO_AUTENTICADO
        )

    payload = authentication_service.decodificar_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=NO_AUTENTICADO
        )

    rut: str | None = payload.get("rut")
    id_sesion: str | None = payload.get("jti")

    if rut is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=NO_AUTENTICADO
        )

    if not id_sesion:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=NO_AUTENTICADO
        )

    sesion = repositorio_sesiones.obtener_por_id(id_sesion)

    if sesion is None or sesion.esta_revocada() or sesion.esta_vencida_ahora():
        # Access token válido criptográficamente pero sin sesión viva: hubo
        # logout, expiró o el usuario fue eliminado. Se responde 401 para que
        # el frontend intente el refresh y caiga al login si también falla.
        audit_service.con_usuario(request.scope, rut, id_sesion)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=NO_AUTENTICADO
        )

    try:
        usuario = use_case.ejecutar(rut)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=NO_AUTENTICADO
        )

    if not usuario.habilitado:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario deshabilitado"
        )

    if usuario.eliminado:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario eliminado"
        )

    # A partir de acá cualquier evento de auditoría de la request ya sabe
    # quién es el actor y desde qué sesión.
    audit_service.con_usuario(request.scope, usuario.rut, id_sesion)
    return usuario
