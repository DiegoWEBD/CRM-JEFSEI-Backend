from fastapi import APIRouter, Depends, status

from app.aplicacion.estado.use_cases.obtener_transiciones_manuales import ObtenerTransicionesManualesUseCase
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.estado.dependencias.deps import get_obtener_transiciones_manuales_use_case
from app.presentacion.api.estado.mappers.transicion_manual_mapper import TransicionManualMapper

router = APIRouter(prefix='/estados', tags=['Estados'])


@router.get('/{codigo_estado}/transiciones-manuales', status_code=status.HTTP_200_OK)
def obtener_transiciones_manuales(
    codigo_estado: str,
    usuario: Usuario = Depends(permisos_requeridos('ADMINISTRAR_PROCESOS_COMERCIALES_PROPIOS')),
    use_case: ObtenerTransicionesManualesUseCase = Depends(get_obtener_transiciones_manuales_use_case)
):
    transiciones = use_case.ejecutar(codigo_estado)

    return {
        'transiciones': TransicionManualMapper(transiciones).map()
    }
