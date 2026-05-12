from fastapi import APIRouter, Depends, HTTPException, status

from app.aplicacion.comuna.use_cases.obtener_comunas import ObtenerComunasUseCase
from app.presentacion.api.comuna.deps import get_obtener_comunas_use_case


router = APIRouter(prefix="/comunas", tags=["Comunas"])

@router.get("/", status_code=status.HTTP_200_OK)
def obtener_comunas(
    use_case: ObtenerComunasUseCase = Depends(get_obtener_comunas_use_case)
):
    try:
        comunas = use_case.ejecutar()

        return {
            "comunas": comunas
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )