from fastapi import APIRouter, Depends, status

from app.aplicacion.plan_pago.use_cases.marcar_pago_cuota import MarcarPagoCuotaUseCase
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.cuota.deps import get_marcar_pago_cuota_use_case


router = APIRouter(prefix='/cuota', tags=['Cuotas'])


@router.post('/{id_cuota}/pagar', status_code=status.HTTP_200_OK)
def marcar_pago_cuota(
    id_cuota: int,
    usuario: Usuario = Depends(permisos_requeridos('MARCAR_PAGO_CUOTA')),
    use_case: MarcarPagoCuotaUseCase = Depends(get_marcar_pago_cuota_use_case)
):
    use_case.ejecutar(id_cuota)

    return {
        'message': 'Cuota marcada como pagada'
    }
