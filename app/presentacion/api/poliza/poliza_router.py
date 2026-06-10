from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.aplicacion.poliza.use_cases.obtener_polizas import ObtenerPolizasUseCase
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.poliza.dependencias.deps import get_obtener_polizas_use_case


router = APIRouter(prefix='/polizas', tags=['Polizas'])

@router.get('/', status_code=status.HTTP_200_OK)
def obtener_polizas(
    id_cliente: int = Query(),
    _ = Depends(permisos_requeridos('OBTENER_POLIZAS')),
    use_case: ObtenerPolizasUseCase = Depends(get_obtener_polizas_use_case)
):
    try:

        polizas = use_case.ejecutar(id_cliente)

        return {
            'polizas': polizas
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )