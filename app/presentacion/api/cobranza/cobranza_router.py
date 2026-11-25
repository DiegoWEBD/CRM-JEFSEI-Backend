from fastapi import APIRouter, Depends

from app.aplicacion.cobranza.use_cases.obtener_dashboard_cobranza import (
    ObtenerDashboardCobranzaUseCase,
)
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.cobranza.dependencias.deps import (
    get_obtener_dashboard_cobranza_use_case,
)
from app.presentacion.api.usuario.lib.usuario_tiene_permiso import (
    usuario_tiene_permiso,
)

router = APIRouter(prefix="/cobranza", tags=["Cobranza"])


@router.get("/dashboard")
def obtener_dashboard_cobranza(
    usuario: Usuario = Depends(
        permisos_requeridos('VER_COBRANZA_PROPIOS', 'VER_COBRANZA_TODOS')
    ),
    use_case: ObtenerDashboardCobranzaUseCase = Depends(
        get_obtener_dashboard_cobranza_use_case
    ),
):
    # VER_COBRANZA_TODOS: dashboard de todos los clientes (sin filtro de cobrador).
    # VER_COBRANZA_PROPIOS: solo los clientes donde el usuario es ejecutivo de cobranza asignado.
    if usuario_tiene_permiso('VER_COBRANZA_TODOS', usuario):
        rut_scoping = None
    else:
        rut_scoping = usuario.rut

    return use_case.ejecutar(rut_scoping)
