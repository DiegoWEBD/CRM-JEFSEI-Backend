from fastapi import APIRouter, Depends, HTTPException, status

from app.aplicacion.evaluacion_proyectos.use_cases.armar_estudio_comercial import ArmarEstudioComercialUseCase
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.estudio_comercial.deps import get_armar_estudio_comercial_use_case
from app.presentacion.api.estudio_comercial.dto.armar_estudio_comercial_request import ArmarEstudioComercialRequest

router = APIRouter(prefix="/estudio-comercial", tags=["Estudio Comercial"])

@router.post("/", status_code = status.HTTP_201_CREATED)
def registrar_usuario(
    request: ArmarEstudioComercialRequest,
    _ = Depends(permisos_requeridos('REGISTRAR_USUARIOS')),
    use_case: ArmarEstudioComercialUseCase = Depends(get_armar_estudio_comercial_use_case)
):
    try:
        estudio_comercial = use_case.ejecutar(
            monto_asegurado_actual=request.monto_asegurado_actual,
            infraseguro_primer_ejemplo=request.infraseguro_primer_ejemplo,
            infraseguro_segundo_ejemplo=request.infraseguro_segundo_ejemplo,
            metros_cuadrados_construidos=request.metros_cuadrados_construidos,
            valor_uf_por_metro_cuadrado=request.valor_uf_por_metro_cuadrado,
            porcentaje_depreciacion=request.porcentaje_depreciacion,
            cantidad_cuotas=request.cantidad_cuotas,
            porcentaje_bienes_espacios_comunes=request.porcentaje_bienes_espacios_comunes
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