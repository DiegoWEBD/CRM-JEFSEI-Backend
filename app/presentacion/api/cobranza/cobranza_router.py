from fastapi import APIRouter, Depends

from app.aplicacion.cobranza.use_cases.obtener_dashboard_cobranza import (
    ObtenerDashboardCobranzaUseCase,
)
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.cobranza.dependencias.deps import (
    get_obtener_dashboard_cobranza_use_case,
)

router = APIRouter(prefix="/cobranza", tags=["Cobranza"])


@router.get("/dashboard")
def obtener_dashboard_cobranza(
    usuario: Usuario = Depends(get_current_user),
    use_case: ObtenerDashboardCobranzaUseCase = Depends(
        get_obtener_dashboard_cobranza_use_case
    ),
):
    return use_case.ejecutar(usuario.rut)
