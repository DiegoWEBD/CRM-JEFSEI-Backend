from typing import Callable
from fastapi import Depends, HTTPException, status, Request
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user


def permisos_prospectos() -> Callable:
    def dependency(
        request: Request,
        usuario = Depends(get_current_user)
    ):
        rut_usuario = request.query_params.get("rut_usuario")
        roles_usuario = getattr(usuario, "roles", [])

        def tiene_permiso(codigo: str) -> bool:
            for rol in roles_usuario:
                for permiso in getattr(rol, "permisos", []):
                    if permiso.codigo == codigo:
                        return True
            return False

        puede_ver_todos = tiene_permiso("OBTENER_PROSPECTOS_TODOS")
        puede_ver_propios = tiene_permiso("OBTENER_PROSPECTOS_PROPIOS")

        if puede_ver_todos:
            return usuario

        if puede_ver_propios:
            if rut_usuario and rut_usuario != usuario.rut:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No puedes consultar prospectos de otro usuario"
                )
            return usuario

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario no autorizado"
        )

    return dependency