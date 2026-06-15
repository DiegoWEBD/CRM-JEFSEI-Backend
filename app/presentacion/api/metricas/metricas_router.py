from fastapi import APIRouter, Depends, HTTPException, status

from app.aplicacion.metricas.use_cases.obtener_prima_vendida_mensual_ej_comercial import ObtenerPrimaVendidaMensualEjComercialUseCase
from app.aplicacion.metricas.use_cases.obtener_progreso_comision_mensual_ej_comercial import ObtenerProgresoComisionMensualEjComercialUseCase
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.metricas.dependencias.deps import get_obtener_prima_vendida_mensual_ej_comercial_use_case, get_obtener_progreso_comision_mensual_ej_comercial_use_case


router = APIRouter(prefix='/metricas', tags=['Metricas'])

@router.get('/ejecutivos-comerciales', status_code=status.HTTP_200_OK)
def obtener_usuarios(
    usuario: Usuario = Depends(get_current_user),
    obtener_prima_vendida_use_case: ObtenerPrimaVendidaMensualEjComercialUseCase = Depends(get_obtener_prima_vendida_mensual_ej_comercial_use_case),
    obtener_progreso_comision_use_case: ObtenerProgresoComisionMensualEjComercialUseCase = Depends(get_obtener_progreso_comision_mensual_ej_comercial_use_case)
):
    try:
        prima_vendida = obtener_prima_vendida_use_case.ejecutar(usuario.rut)
        comision = obtener_progreso_comision_use_case.ejecutar(usuario)

        return {
            'prima_vendida': prima_vendida,
            'meta_mensual': usuario.meta_mensual_uf,
            'comision': comision
        }
    
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )
    
    