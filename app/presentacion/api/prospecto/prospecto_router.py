from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.aplicacion.prospecto.servicios.consulta_prospectos_service import ConsultaProspectosService
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.prospecto.deps import get_consulta_prospectos_service, get_registrar_prospecto_use_case
from app.presentacion.api.prospecto.dto.registrar_prospecto_request import RegistrarProspectoRequest


router = APIRouter(prefix="/prospectos", tags=["Prospectos"])

@router.get("/", status_code=status.HTTP_200_OK)
def obtener_prospectos(
    rut_usuario: Optional[str] = Query(None),
    usuario: Usuario = Depends(get_current_user),
    consulta_prospectos_service: ConsultaProspectosService = Depends(get_consulta_prospectos_service)
):
    try:
        
        def tiene_permiso(codigo: str) -> bool:
            for rol in usuario.roles:
                for permiso in rol.permisos:
                    if permiso.codigo == codigo:
                        return True
            return False

        puede_ver_todos = tiene_permiso("OBTENER_PROSPECTOS_TODOS")
        puede_ver_propios = tiene_permiso("OBTENER_PROSPECTOS_PROPIOS")

        # GET /prospectos?rut_usuario=xxxxx
        if rut_usuario:

            if puede_ver_todos:
                prospectos = consulta_prospectos_service.obtener_todos(rut_usuario)

            elif puede_ver_propios:

                if rut_usuario != usuario.rut:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Usuario no autorizado"
                    )

                prospectos = consulta_prospectos_service.obtener_todos(rut_usuario)

            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Usuario no autorizado"
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
                    detail="Usuario no autorizado"
                )

        return {
            "data": prospectos
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )
    
@router.post('/', status_code=status.HTTP_201_CREATED)
def registrar_prospecto(
    request: RegistrarProspectoRequest,
    usuario: Usuario = Depends(permisos_requeridos('REGISTRAR_PROSPECTO')),
    use_case = Depends(get_registrar_prospecto_use_case)
):
    try:
        use_case.ejecutar(
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

        return {
            "message": "Prospecto registrado correctamente"
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )