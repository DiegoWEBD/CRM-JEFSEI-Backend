from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.aplicacion.proceso_comercial.use_cases.obtener_procesos_comerciales import ObtenerProcesosComercialesUseCase
from app.aplicacion.prospecto.use_cases.obtener_prospecto import ObtenerProspectoUseCase
from app.aplicacion.solicitud_cotizacion.servicios.consulta_solicitudes_cotizacion_service import ConsultaSolicitudesCotizacionService
from app.aplicacion.solicitud_cotizacion.use_cases.obtener_solicitudes_cotizacion_activas import ObtenerSolicitudesCotizacionActivasUseCase
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.prospecto.dependencias.deps import get_obtener_prospecto_use_case
from app.presentacion.api.solicitud_cotizacion.dependencias.deps import get_consulta_solicitudes_cotizacion_service, get_obtener_procesos_comerciales_use_case, get_obtener_solicitudes_cotizacion_activas_use_case
from app.presentacion.api.usuario.lib.usuario_tiene_permiso import usuario_tiene_permiso


router = APIRouter(prefix='/solicitudes-cotizacion', tags=['SolicitudesCotizacion'])

@router.get('/', status_code=status.HTTP_200_OK)
def obtener_solicitudes(
    id_prospecto: Optional[int] = Query(None),
    usuario: Usuario = Depends(permisos_requeridos('VER_SOLICITUDES_COTIZACION_PROPIAS', 'VER_SOLICITUDES_COTIZACION_GLOBAL')),
    obtener_prospecto_use_case: ObtenerProspectoUseCase = Depends(get_obtener_prospecto_use_case),
    obtener_procesos_comerciales_use_case: ObtenerProcesosComercialesUseCase = Depends(get_obtener_procesos_comerciales_use_case),
    solicitudes_activas_use_case: ObtenerSolicitudesCotizacionActivasUseCase = Depends(get_obtener_solicitudes_cotizacion_activas_use_case),
    consulta_solicitudes_service: ConsultaSolicitudesCotizacionService = Depends(get_consulta_solicitudes_cotizacion_service)
):
    try:
        puede_ver_todas = usuario_tiene_permiso('VER_SOLICITUDES_COTIZACION_GLOBAL', usuario)
        solicitudes = []

        if id_prospecto is not None:

            es_propio = False
            prospecto = obtener_prospecto_use_case.ejecutar(id_prospecto)
            
            if prospecto.registrado_por.rut == usuario.rut:
                es_propio = True
            if prospecto.ejecutivo_comercial_asignado and prospecto.ejecutivo_comercial_asignado.rut == usuario.rut:
                es_propio = True

            procesos_comerciales = obtener_procesos_comerciales_use_case.ejecutar(id_prospecto)

            for proceso in procesos_comerciales:
                if proceso.ejecutivo_comercial and proceso.ejecutivo_comercial.rut == usuario.rut:
                    es_propio = True
                if proceso.ejecutivo_evaluacion and proceso.ejecutivo_evaluacion.rut == usuario.rut:
                    es_propio = True

            if not es_propio and not puede_ver_todas:
                raise UsuarioNoAutorizadoException

            solicitudes = solicitudes_activas_use_case.ejecutar(id_prospecto)

        else:
            rut_usuario = None if puede_ver_todas else usuario.rut
            solicitudes = consulta_solicitudes_service.obtener_todas(rut_usuario)

        return {
            'solicitudes': solicitudes
        }
    
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )
    
    except UsuarioNoAutorizadoException as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
    

@router.post('/', status_code=status.HTTP_200_OK)
def solicitar_cotizacion(
    usuario: Usuario = Depends(permisos_requeridos('SOLICITAR_COTIZACION')),
):
    pass