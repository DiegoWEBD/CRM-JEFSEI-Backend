from fastapi import APIRouter, Depends, status

from app.aplicacion.prospecto.use_cases.asignar_ejecutivo_cobranza import AsignarEjecutivoCobranzaUseCase
from app.aplicacion.prospecto.use_cases.asignar_ejecutivo_renovacion import AsignarEjecutivoRenovacionUseCase
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.cliente.dependencias.deps import get_asignar_ejecutivo_cobranza_use_case, get_asignar_ejecutivo_renovacion_use_case
from app.presentacion.api.cliente.dto.requests.asignar_ejecutivo_cobranza_request import AsignarEjecutivoCobranzaRequest
from app.presentacion.api.cliente.dto.requests.asignar_ejecutivo_renovacion_request import AsignarEjecutivoRenovacionRequest


router = APIRouter(prefix='/clientes', tags=['Clientes'])


@router.post('/{id_cliente}/asignar-ej-cobranza', status_code=status.HTTP_200_OK)
def asignar_ejecutivo_cobranza(
    id_cliente: int,
    request: AsignarEjecutivoCobranzaRequest,
    usuario: Usuario = Depends(permisos_requeridos('ASIGNAR_EJECUTIVO_COBRANZA')),
    use_case: AsignarEjecutivoCobranzaUseCase = Depends(get_asignar_ejecutivo_cobranza_use_case)
):
    use_case.ejecutar(
        id_cliente=id_cliente,
        rut_ej_cobranza=request.rut_ej_cobranza,
        asignado_por=usuario
    )

    return {
        'message': 'Ejecutivo de cobranza asignado correctamente'
    }


@router.post('/{id_cliente}/asignar-ej-renovacion', status_code=status.HTTP_200_OK)
def asignar_ejecutivo_renovacion(
    id_cliente: int,
    request: AsignarEjecutivoRenovacionRequest,
    usuario: Usuario = Depends(permisos_requeridos('ASIGNAR_EJECUTIVO_RENOVACION')),
    use_case: AsignarEjecutivoRenovacionUseCase = Depends(get_asignar_ejecutivo_renovacion_use_case)
):
    use_case.ejecutar(
        id_cliente=id_cliente,
        rut_ej_renovacion=request.rut_ej_renovacion,
        asignado_por=usuario
    )

    return {
        'message': 'Ejecutivo de renovación asignado correctamente'
    }
