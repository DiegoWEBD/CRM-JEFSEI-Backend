from fastapi import Depends, HTTPException, status
from typing import Callable

from app.presentacion.api.auth.dependencias.get_current_user import get_current_user


def permisos_requeridos(*permisos_permitidos: str) -> Callable:
    def dependency(usuario = Depends(get_current_user)):
        
        roles_usuario = getattr(usuario, "roles", [])

        for rol in roles_usuario:
            for permiso in getattr(rol, "permisos", []):
                if permiso.codigo in permisos_permitidos:
                    return usuario

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario no autorizado"
        )

    return dependency