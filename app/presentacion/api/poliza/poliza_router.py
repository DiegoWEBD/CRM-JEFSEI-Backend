from fastapi import APIRouter, Depends, Query, status

from app.aplicacion.cotizacion.use_cases.registrar_renovacion_cotizada import RegistrarRenovacionCotizadaUseCase
from app.aplicacion.plan_pago.use_cases.obtener_plan_pago_poliza import ObtenerPlanPagoPolizaUseCase
from app.aplicacion.poliza.use_cases.obtener_poliza import ObtenerPolizaUseCase
from app.aplicacion.poliza.use_cases.obtener_polizas import ObtenerPolizasUseCase
from app.dominio.usuario.usuario import Usuario
from app.infraestructura.poliza.adapadores.poliza_json_adapter import PolizaJsonAdapter
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.plan_pago.dependencias.deps import get_obtener_plan_pago_poliza_use_case
from app.presentacion.api.poliza.dependencias.deps import get_obtener_poliza_use_case, get_obtener_polizas_use_case, get_registrar_renovacion_cotizada_use_case


router = APIRouter(prefix='/polizas', tags=['Polizas'])

@router.get('/', status_code=status.HTTP_200_OK)
def obtener_polizas(
    id_cliente: int = Query(),
    usuario: Usuario = Depends(permisos_requeridos('OBTENER_POLIZAS_TODAS', 'OBTENER_POLIZAS_PROPIAS')),
    use_case: ObtenerPolizasUseCase = Depends(get_obtener_polizas_use_case)
):
    rut_usuario = usuario.rut

    for rol in usuario.roles:
        for permiso in rol.permisos:
            if permiso.codigo == 'OBTENER_POLIZAS_TODAS':
                rut_usuario = None

    polizas = use_case.ejecutar(id_cliente, rut_usuario)

    return {
        'polizas': [PolizaJsonAdapter(poliza).to_json() for poliza in polizas]
    }

@router.get('/{numero_poliza}', status_code=status.HTTP_200_OK)
def obtener_poliza(
    numero_poliza: str,
    usuario: Usuario = Depends(permisos_requeridos('OBTENER_POLIZAS_TODAS', 'OBTENER_POLIZAS_PROPIAS')),
    use_case: ObtenerPolizaUseCase = Depends(get_obtener_poliza_use_case)
):
    poliza = use_case.ejecutar(numero_poliza, usuario)

    return {
        'poliza': PolizaJsonAdapter(poliza).to_json()
    }


@router.post('/{numero_poliza}/registrar-renovacion-cotizada', status_code=status.HTTP_201_CREATED)
def registrar_renovacion_cotizada(
    numero_poliza: str,
    usuario: Usuario = Depends(permisos_requeridos('CARGAR_COTIZACIONES')),
    use_case: RegistrarRenovacionCotizadaUseCase = Depends(get_registrar_renovacion_cotizada_use_case)
):
    use_case.ejecutar(numero_poliza, usuario.rut)

    return {
        'message': 'Cotización para renovación de póliza registrada'
    }


@router.get('/{numero_poliza}/plan-pago', status_code=status.HTTP_200_OK)
def obtener_plan_pago(
    numero_poliza: str,
    usuario: Usuario = Depends(permisos_requeridos('VER_PLAN_PAGO_GLOBAL', 'VER_PLAN_PAGO_PROPIOS')),
    use_case: ObtenerPlanPagoPolizaUseCase = Depends(get_obtener_plan_pago_poliza_use_case)
):
    plan_pago = use_case.ejecutar(numero_poliza, usuario)

    return {
        'plan_pago': plan_pago
    }