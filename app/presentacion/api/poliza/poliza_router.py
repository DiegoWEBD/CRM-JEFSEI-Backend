from fastapi import APIRouter, Depends, Query, status

from app.aplicacion.cotizacion.use_cases.registrar_renovacion_cotizada import RegistrarRenovacionCotizadaUseCase
from app.aplicacion.poliza.use_cases.obtener_polizas import ObtenerPolizasUseCase
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.poliza.dependencias.deps import get_obtener_polizas_use_case, get_registrar_renovacion_cotizada_use_case


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
        'polizas': polizas
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