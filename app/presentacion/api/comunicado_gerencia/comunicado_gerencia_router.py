from fastapi import APIRouter, Depends, HTTPException, status

from app.aplicacion.comunicado_gerencia.use_cases.obtener_comunicados_gerencia import ObtenerComunicadosGerenciaUseCase
from app.aplicacion.comunicado_gerencia.use_cases.registrar_comunicado_gerencia import RegistrarComunicadoGerenciaUseCase
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.comunicado_gerencia.dependencias.deps import get_obtener_comunicados_gerencia_use_case, get_registrar_comunicado_gerencia_use_case
from app.presentacion.api.comunicado_gerencia.dto.registrar_comunicado_request import RegistrarComunicadoRequest


router = APIRouter(prefix='/comunicados-gerencia', tags=['ComunicadosGerencia'])

@router.get('/', status_code=status.HTTP_200_OK)
def obtener_comunicados_gerencia(
    use_case: ObtenerComunicadosGerenciaUseCase = Depends(get_obtener_comunicados_gerencia_use_case)
):
    comunicados = use_case.ejecutar()

    return {
        'comunicados': comunicados
    }


@router.post('/', status_code=status.HTTP_201_CREATED)
def registrar_comunicado_gerencia(
    request: RegistrarComunicadoRequest,
    _ = Depends(permisos_requeridos('CREAR_COMUNICADO')),
    usuario: Usuario = Depends(get_current_user),
    use_case: RegistrarComunicadoGerenciaUseCase = Depends(get_registrar_comunicado_gerencia_use_case)
):
    registrado = use_case.ejecutar(
        usuario=usuario,
        titulo=request.titulo,
        descripcion=request.descripcion,
        prioridad=request.prioridad,
        caducidad=request.caducidad
    )

    if not registrado:
        raise HTTPException(
            status_code=400,
            detail='Error al registrar el comunicado'
        )

    return {
        'message': 'Comunicado registrado correctamente'
    }