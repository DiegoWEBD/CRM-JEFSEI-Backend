from fastapi import APIRouter, Depends, HTTPException, status

from app.aplicacion.comunicado_gerencia.use_cases.obtener_comunicados_gerencia import ObtenerComunicadosGerenciaUseCase
from app.presentacion.api.comunicado_gerencia.dependencias.deps import get_obtener_comunicados_gerencia_use_case


router = APIRouter(prefix='/comunicados-gerencia', tags=['ComunicadosGerencia'])

@router.get('/', status_code=status.HTTP_200_OK)
def obtener_comunicados_gerencia(
    use_case: ObtenerComunicadosGerenciaUseCase = Depends(get_obtener_comunicados_gerencia_use_case)
):
    try:
        comunicados = use_case.ejecutar()

        return {
            'comunicados': comunicados
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )