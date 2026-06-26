from fastapi import APIRouter, Depends, status

from app.aplicacion.sucursal.use_cases.obtener_sucursales import ObtenerSucursalesUseCase
from app.presentacion.api.sucursal.dependencias.deps import get_obtener_sucursales_use_case


router = APIRouter(prefix='/sucursales', tags=['Sucursales'])

@router.get('/', status_code=status.HTTP_200_OK)
def obtener_sucursales(
    use_case: ObtenerSucursalesUseCase = Depends(get_obtener_sucursales_use_case)
):
    sucursales = use_case.ejecutar()

    return {
        'sucursales': sucursales
    }