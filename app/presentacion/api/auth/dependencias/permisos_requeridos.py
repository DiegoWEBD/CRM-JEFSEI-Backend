from typing import Callable

from fastapi import Depends, HTTPException, Request, status

from app.aplicacion.auditoria.audit_service import AuditService
from app.dominio.auditoria.enums import Categoria, Resultado, TipoEvento
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.auth.dependencias.get_sesion_use_cases import get_audit_service

AUTHORIZATION_DENIED = 'AUTHORIZATION_DENIED'


def permisos_requeridos(*permisos_permitidos: str) -> Callable:
    """Exige al menos uno de los permisos indicados.

    Un 403 es un intento de acceso no autorizado y se audita siempre: es de los
    eventos que más interesta detectar. El log no registra los roles del
    usuario para no duplicar información ni exponerla.
    """

    def dependency(
        request: Request,
        usuario=Depends(get_current_user),
        audit_service: AuditService = Depends(get_audit_service),
    ):
        roles_usuario = getattr(usuario, 'roles', [])

        for rol in roles_usuario:
            for permiso in getattr(rol, 'permisos', []):
                if permiso.codigo in permisos_permitidos:
                    return usuario

        audit_service.log(
            event_type=TipoEvento.AUTHORIZATION_DENIED,
            category=Categoria.SECURITY,
            result=Resultado.DENIED,
            scope=request.scope,
            description='Acceso denegado por permisos insuficientes',
            error_code=AUTHORIZATION_DENIED,
            status_http=status.HTTP_403_FORBIDDEN,
            metadata={
                'permisos_requeridos': list(permisos_permitidos),
                'path': request.url.path,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Usuario no autorizado'
        )

    return dependency
