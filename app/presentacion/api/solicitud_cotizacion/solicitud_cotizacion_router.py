from fastapi import APIRouter, Depends, status
from app.aplicacion.cotizacion.use_cases.obtener_cotizaciones_por_solicitud import ObtenerCotizacionesPorSolicitudUseCase
from app.aplicacion.cotizacion.use_cases.registrar_cotizacion_a_solicitud import RegistrarCotizacionASolicitudUseCase
from app.aplicacion.prospecto.use_cases.obtener_prospecto import ObtenerProspectoUseCase
from app.aplicacion.solicitud_cotizacion.servicios.consulta_solicitudes_cotizacion_service import ConsultaSolicitudesCotizacionService
from app.aplicacion.solicitud_cotizacion.use_cases.obtener_resumen_solicitudes_cotizacion_activas import ObtenerResumenSolicitudesCotizacionActivasUseCase
from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.solicitar_cotizacion import SolicitarCotizacionUseCase
from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.solicitar_recotizacion import SolicitarRecotizacionUseCase
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.usuario.usuario import Usuario
from app.infraestructura.cotizacion.adaptadores.cotizacion_json_adapter import CotizacionJsonAdapter
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.cotizacion.dependencias.deps import get_obtener_cotizaciones_por_solicitud_use_case, get_registrar_cotizacion_a_solicitud_use_case
from app.presentacion.api.exceptions.bad_request_exception import BadRequestException
from app.presentacion.api.prospecto.dependencias.deps import get_obtener_prospecto_use_case
from app.presentacion.api.solicitud_cotizacion.dependencias.deps import get_consulta_solicitudes_cotizacion_service, get_obtener_resumen_solicitudes_cotizacion_activas_use_case, get_solicitar_cotizacion_use_case, get_solicitar_recotizacion_use_case
from app.presentacion.api.solicitud_cotizacion.dto.requests.registrar_cotizacion_a_solicitud_request import RegistrarCotizacionASolicitudRequest
from app.presentacion.api.solicitud_cotizacion.dto.requests.solicitud_cotizacion_request_union import SolicitudCotizacionRequestUnion
from app.presentacion.api.usuario.lib.usuario_tiene_permiso import usuario_tiene_permiso


router = APIRouter(prefix='/solicitudes-cotizacion', tags=['SolicitudesCotizacion'])

@router.get('/', status_code=status.HTTP_200_OK)
def obtener_solicitudes(
    usuario: Usuario = Depends(permisos_requeridos('VER_SOLICITUDES_COTIZACION_PROPIAS', 'VER_SOLICITUDES_COTIZACION_GLOBAL')),
    use_case: ObtenerResumenSolicitudesCotizacionActivasUseCase = Depends(get_obtener_resumen_solicitudes_cotizacion_activas_use_case)
):
    puede_ver_todas = usuario_tiene_permiso('VER_SOLICITUDES_COTIZACION_GLOBAL', usuario)
    solicitudes = []

    rut_usuario = None if puede_ver_todas else usuario.rut
    solicitudes = use_case.ejecutar(rut_usuario)

    return {
        'solicitudes': solicitudes
    }
    

@router.post('/', status_code=status.HTTP_201_CREATED)
def solicitar_cotizacion(
    request: SolicitudCotizacionRequestUnion,
    usuario: Usuario = Depends(permisos_requeridos('SOLICITAR_COTIZACION')),
    obtener_prospecto_use_case: ObtenerProspectoUseCase = Depends(get_obtener_prospecto_use_case),
    solicitar_cotizacion_use_case: SolicitarCotizacionUseCase = Depends(get_solicitar_cotizacion_use_case)
):
    autorizado = False
    prospecto = obtener_prospecto_use_case.ejecutar(request.id_prospecto)
    
    if prospecto.ejecutivo_comercial_asignado and prospecto.ejecutivo_comercial_asignado.rut == usuario.rut:
        autorizado = True

    if not autorizado:
        raise UsuarioNoAutorizadoException

    solicitar_cotizacion_use_case.ejecutar(request, usuario)

    return {
        'message': 'Solicitud de cotización registrada'
    }

@router.post('/{id}/recotizacion', status_code=status.HTTP_201_CREATED)
def solicitar_recotizacion(
    id: int,
    request: SolicitudCotizacionRequestUnion,
    usuario: Usuario = Depends(permisos_requeridos('SOLICITAR_COTIZACION')),
    obtener_prospecto_use_case: ObtenerProspectoUseCase = Depends(get_obtener_prospecto_use_case),
    solicitar_cotizacion_use_case: SolicitarRecotizacionUseCase = Depends(get_solicitar_recotizacion_use_case)
):
    if request.motivo_recotizacion is None:
        raise BadRequestException('Debe indicar motivo_recotizacion')

    autorizado = False
    prospecto = obtener_prospecto_use_case.ejecutar(request.id_prospecto)
    
    if prospecto.ejecutivo_comercial_asignado and prospecto.ejecutivo_comercial_asignado.rut == usuario.rut:
        autorizado = True

    if not autorizado:
        raise UsuarioNoAutorizadoException

    solicitar_cotizacion_use_case.ejecutar(
        request=request,
        id_solicitud_original=id,
        usuario=usuario
    )

    return {
        'message': 'Recotización solicitada'
    }
    
@router.get('/{id}/cotizaciones', status_code=status.HTTP_200_OK)
def obtener_cotizaciones_por_solicitud(
    id: int,
    usuario: Usuario = Depends(permisos_requeridos('VER_COTIZACIONES_GLOBAL', 'VER_COTIZACIONES_PROPIAS')),
    use_case: ObtenerCotizacionesPorSolicitudUseCase = Depends(get_obtener_cotizaciones_por_solicitud_use_case)
):
    rut_usuario = usuario.rut if not usuario_tiene_permiso('VER_COTIZACIONES_GLOBAL', usuario) else None
    cotizaciones = use_case.ejecutar(id, rut_usuario)

    return {
        'cotizaciones': [CotizacionJsonAdapter(cotizacion).to_cotizacion_json() for cotizacion in cotizaciones]
    } 


@router.post('/{id}/cotizaciones', status_code=status.HTTP_201_CREATED)
def registrar_cotizacion_a_solicitud(
    id: int,
    request: RegistrarCotizacionASolicitudRequest,
    usuario: Usuario = Depends(permisos_requeridos('CARGAR_COTIZACIONES')),
    use_case: RegistrarCotizacionASolicitudUseCase = Depends(get_registrar_cotizacion_a_solicitud_use_case)
):
    use_case.ejecutar(
        rut_usuario=usuario.rut,
        id_solicitud=id,
        monto_total_asegurado=request.monto_total_asegurado,
        tasa_afecta=request.tasa_afecta,
        tasa_excenta=request.tasa_excenta,
        tasa_politica=request.tasa_politica,
        prima_adicional_asistencia=request.prima_adicional_asistencia,
        id_company=request.id_company,
        fecha_emision=request.fecha_emision,
        fecha_vencimiento=request.fecha_vencimiento
    )

    return {
        'message': 'Cotización registrada'
    }