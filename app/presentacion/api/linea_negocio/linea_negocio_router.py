from fastapi import APIRouter, Depends

from app.aplicacion.linea_negocio.use_cases.obtener_lineas_de_negocio import ObtenerLineasDeNegocioUseCase
from app.aplicacion.linea_negocio.use_cases.obtener_productos_linea_negocio import ObtenerProductosLineaNegocioUseCase
from app.presentacion.api.linea_negocio.deps import get_obtener_lineas_negocio_use_case, get_obtener_productos_linea_negocio_use_case


router = APIRouter(prefix="/lineas-negocio", tags=["Lineas de Negocio"])

@router.get("/", status_code=200)
def obtener_lineas_negocio(
    use_case: ObtenerLineasDeNegocioUseCase = Depends(get_obtener_lineas_negocio_use_case)
):
    lineas_negocio = use_case.ejecutar()
    
    return {
        "lineas_negocio": lineas_negocio
    }


@router.get("/{id}/productos", status_code=200)
def obtener_productos_linea_negocio(
    id: int,
    use_case: ObtenerProductosLineaNegocioUseCase = Depends(get_obtener_productos_linea_negocio_use_case)
):
    productos = use_case.ejecutar(id)

    return {
        "productos": productos
    }