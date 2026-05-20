from fastapi import APIRouter, Depends, HTTPException, status

from app.aplicacion.evaluacion_proyectos.use_cases.armar_estudio_comercial_condominio import ArmarEstudioComercialCondominioUseCase
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.estudio_comercial.deps import get_armar_estudio_comercial_use_case
from app.presentacion.api.estudio_comercial.dto.armar_estudio_comercial_request import ArmarEstudioComercialRequest

router = APIRouter(prefix="/estudio-comercial", tags=["Estudio Comercial"])

@router.post("/", status_code = status.HTTP_201_CREATED)
def registrar_usuario(
    request: ArmarEstudioComercialRequest,
    _ = Depends(permisos_requeridos('ARMAR_ESTUDIO_COMERCIAL')),
    use_case: ArmarEstudioComercialCondominioUseCase = Depends(get_armar_estudio_comercial_use_case)
):
    try:
        estudio_comercial = use_case.ejecutar(
            id_prospecto=request.id_prospecto,
            infraseguro_primer_ejemplo=request.infraseguro_primer_ejemplo,
            infraseguro_segundo_ejemplo=request.infraseguro_segundo_ejemplo,
            cantidad_cuotas=request.cantidad_cuotas,
            id_companies=request.id_companies
        )

        return {
            "estudio_comercial": estudio_comercial
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )