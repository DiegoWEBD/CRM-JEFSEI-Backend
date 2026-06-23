from fastapi import APIRouter, Depends, status

from app.aplicacion.administrador_condominio.use_cases.obtener_administrador_por_id import (
    ObtenerAdministradorPorIdUseCase,
)
from app.aplicacion.administrador_condominio.use_cases.obtener_administradores import (
    ObtenerAdministradoresUseCase,
)
from app.aplicacion.prospecto.servicios.consulta_prospectos_service import (
    ConsultaProspectosService,
)
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.usuario.usuario import Usuario
from app.infraestructura.administrador_condominio.adaptadores.administrador_condominio_json_adapter import (
    AdministradorCondominioJsonAdapter,
)
from app.presentacion.api.administrador_condominio.deps import (
    get_consulta_prospectos_service,
    get_obtener_administrador_por_id_use_case,
    get_obtener_administradores_use_case,
)
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.usuario.lib.usuario_tiene_permiso import (
    usuario_tiene_permiso,
)


router = APIRouter(prefix="/administradores", tags=["Administradores"])


@router.get("/{id}", status_code=status.HTTP_200_OK)
def obtener_administrador_por_id(
    id: int,
    use_case: ObtenerAdministradorPorIdUseCase = Depends(
        get_obtener_administrador_por_id_use_case
    ),
):
    administrador = use_case.ejecutar(id)
    return {
        "data": AdministradorCondominioJsonAdapter(administrador).to_json()
    }


@router.get("/", status_code=status.HTTP_200_OK)
def obtener_administradores(
    use_case: ObtenerAdministradoresUseCase = Depends(
        get_obtener_administradores_use_case
    ),
):
    administradores = use_case.ejecutar()

    return {
        "data": [
            AdministradorCondominioJsonAdapter(a).to_json()
            for a in administradores
        ]
    }


@router.get("/{id}/prospectos", status_code=status.HTTP_200_OK)
def obtener_prospectos_por_administrador(
    id: int,
    usuario: Usuario = Depends(get_current_user),
    obtener_administrador: ObtenerAdministradorPorIdUseCase = Depends(
        get_obtener_administrador_por_id_use_case
    ),
    consulta_service: ConsultaProspectosService = Depends(
        get_consulta_prospectos_service
    ),
):
    obtener_administrador.ejecutar(id)

    puede_ver_todos = usuario_tiene_permiso("OBTENER_PROSPECTOS_TODOS", usuario)
    puede_ver_propios = usuario_tiene_permiso(
        "OBTENER_PROSPECTOS_PROPIOS", usuario
    )

    if puede_ver_todos:
        prospectos = consulta_service.obtener_por_administrador(id)

    elif puede_ver_propios:
        prospectos = consulta_service.obtener_por_administrador(
            id, usuario.rut
        )

    else:
        raise UsuarioNoAutorizadoException()

    return {"data": prospectos}
