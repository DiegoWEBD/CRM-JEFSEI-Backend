from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.aplicacion.linea_negocio.use_cases.obtener_linea_negocio_prospecto import ObtenerLineaNegocioProspectoUseCase
from app.aplicacion.prospecto.servicios.consulta_prospectos_service import ConsultaProspectosService
from app.presentacion.api.prospecto.dependencias.obtener_prospecto_factory import ObtenerProspectoFactory
from app.aplicacion.prospecto.use_cases.asignar_ejecutivo_comercial import AsignarEjecutivoComercialUseCase
from app.aplicacion.prospecto.use_cases.asignar_ejecutivo_evaluacion import AsignarEjecutivoEvaluacionUseCase
from app.aplicacion.prospecto.use_cases.registrar_prospecto import RegistrarProspectoUseCase
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.prospecto.dependencias.deps import get_asignar_ejecutivo_comercial_use_case, get_asignar_ejecutivo_evaluacion_use_case, get_consulta_prospectos_service, get_obtener_linea_negocio_prospecto_use_case, get_obtener_prospecto_factory, get_registrar_prospecto_use_case
from app.presentacion.api.prospecto.dto.requests.asignar_ejecutivo_comercial_request import AsignarEjecutivoComercialRequest
from app.presentacion.api.prospecto.dto.requests.asignar_ejecutivo_evaluacion_request import AsignarEjecutivoEvaluacionRequest
from app.presentacion.api.prospecto.dto.requests.registrar_prospecto_request import RegistrarProspectoRequest
from app.presentacion.api.prospecto.lib.tiene_permisos_prospecto import tiene_permisos_prospecto
from app.presentacion.api.usuario.lib.usuario_tiene_permiso import usuario_tiene_permiso


router = APIRouter(prefix='/prospectos', tags=['Prospectos'])

@router.get('/', status_code=status.HTTP_200_OK)
def obtener_prospectos(
    rut_usuario: Optional[str] = Query(None),
    usuario: Usuario = Depends(get_current_user),
    consulta_prospectos_service: ConsultaProspectosService = Depends(get_consulta_prospectos_service)
):
    try:

        puede_ver_todos = usuario_tiene_permiso('OBTENER_PROSPECTOS_TODOS', usuario)
        puede_ver_propios = usuario_tiene_permiso('OBTENER_PROSPECTOS_PROPIOS', usuario)
        prospectos = []

        # GET /prospectos?rut_usuario=xxxxx
        if rut_usuario:

            if puede_ver_todos:
                prospectos = consulta_prospectos_service.obtener_todos(rut_usuario)

            elif puede_ver_propios:

                if rut_usuario != usuario.rut:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail='Usuario no autorizado'
                    )

                prospectos = consulta_prospectos_service.obtener_todos(rut_usuario)

            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='Usuario no autorizado'
                )

        # GET /prospectos
        else:

            if puede_ver_todos:
                prospectos = consulta_prospectos_service.obtener_todos()

            elif puede_ver_propios:
                prospectos = consulta_prospectos_service.obtener_todos(usuario.rut)

            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='Usuario no autorizado'
                )

        return {
            'data': prospectos
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )
    

@router.get('/{id}', status_code=status.HTTP_200_OK)
def obtener_prospecto_por_id(
    id: int,
    usuario: Usuario = Depends(permisos_requeridos('OBTENER_PROSPECTOS_PROPIOS', 'OBTENER_PROSPECTOS_TODOS')),
    obtener_linea_negocio_prospecto: ObtenerLineaNegocioProspectoUseCase = Depends(get_obtener_linea_negocio_prospecto_use_case),
    obtener_prospecto_factory: ObtenerProspectoFactory = Depends(get_obtener_prospecto_factory)
):
    try:
        linea_negocio = obtener_linea_negocio_prospecto.ejecutar(id)

        prospecto = obtener_prospecto_factory.obtener(
            linea_negocio=linea_negocio.nombre,
            id_prospecto=id
        )

        autorizado = tiene_permisos_prospecto(usuario=usuario, prospecto=prospecto)  

        if not autorizado:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Usuario no autorizado'
            ) 

        adapter = obtener_prospecto_factory.obtener_adapter(linea_negocio.nombre)  

        return {
            'prospecto': adapter(prospecto).to_prospecto_json()
        }
        

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )

    
@router.post('/', status_code=status.HTTP_201_CREATED)
def registrar_prospecto(
    request: RegistrarProspectoRequest,
    usuario: Usuario = Depends(permisos_requeridos('REGISTRAR_PROSPECTO')),
    registrar_prospecto: RegistrarProspectoUseCase = Depends(get_registrar_prospecto_use_case),
    asignar_ejecutivo_comercial: AsignarEjecutivoComercialUseCase = Depends(get_asignar_ejecutivo_comercial_use_case)
):
    try:
        ROL_EJECUTIVO_COMERCIAL = 'EJECUTIVO_COMERCIAL'

        id_prospecto = registrar_prospecto.ejecutar(
            rut_usuario=usuario.rut,
            rut_riesgo=request.rut_riesgo,
            nombre_riesgo=request.nombre_riesgo,
            nombre_contacto=request.nombre_contacto,
            telefono_contacto=request.telefono_contacto,
            correo_contacto=request.correo_contacto,
            direccion=request.direccion,
            id_comuna=request.id_comuna,
            observaciones=request.observaciones,
            id_linea_negocio=request.id_linea_negocio,
            cargo_contacto=request.cargo_contacto,
            tiene_locales_comerciales=request.tiene_locales_comerciales,
            uso_del_condominio=request.uso_del_condominio,
            numero_pisos=request.numero_pisos,
            numero_torres=request.numero_torres,
            cantidad_departamentos=request.cantidad_departamentos,
            cantidad_subterraneos=request.cantidad_subterraneos,
            tiene_piscina=request.tiene_piscina,
            year_construccion=request.year_construccion,
            metros_cuadrados=request.metros_cuadrados,
            desea_ser_contactado=request.desea_ser_contactado
        )

        es_ejecutivo_comercial = False

        for rol in usuario.roles:
            if rol.nombre == ROL_EJECUTIVO_COMERCIAL:
                es_ejecutivo_comercial = True

        if es_ejecutivo_comercial:
            asignar_ejecutivo_comercial.ejecutar(
                id_prospecto=id_prospecto,
                rut_ej_comercial=usuario.rut,
                asignado_por=usuario
            )

        return {
            'message': 'Prospecto registrado correctamente'
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
    

@router.post('/{id}/asignar-ej-comercial', status_code=status.HTTP_200_OK)
def asignar_ejecutivo_comercial(
    id: int,
    request: AsignarEjecutivoComercialRequest,
    usuario = Depends(permisos_requeridos('ASIGNAR_EJECUTIVO_COMERCIAL')),
    use_case: AsignarEjecutivoComercialUseCase = Depends(get_asignar_ejecutivo_comercial_use_case)
):
    try:
        use_case.ejecutar(
            id_prospecto=id, 
            rut_ej_comercial=request.rut_ej_comercial,
            asignado_por=usuario
        )

        return {
            'message': 'Ejecutivo comercial asignado correctamente'
        }

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )


@router.post('/{id}/asignar-ej-evaluacion', status_code=status.HTTP_200_OK)
def asignar_ejecutivo_evaluacion(
    id: int,
    request: AsignarEjecutivoEvaluacionRequest,
    _ = Depends(permisos_requeridos('ASIGNAR_EJECUTIVO_EVALUACION')),
    use_case: AsignarEjecutivoEvaluacionUseCase = Depends(get_asignar_ejecutivo_evaluacion_use_case)
):
    try:
        use_case.ejecutar(
            id_prospecto=id, 
            rut_ej_evaluacion=request.rut_ej_evaluacion
        )

        return {
            'message': 'Ejecutivo de evaluación de proyectos asignado correctamente'
        }

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )

