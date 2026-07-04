from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.aplicacion.recordatorio.use_cases.obtener_recordatorios import ObtenerRecordatoriosUsuarioUseCase
from app.aplicacion.recordatorio.use_cases.registrar_recordatorio import RegistrarRecordatorioUseCase
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.recordatorio.dependencias.deps import get_obtener_recordatorios_usuario_use_case, get_registrar_recordatorio_use_case
from app.presentacion.api.recordatorio.dto.registrar_recordatorio_request import RegistrarRecordatorioRequest


router = APIRouter(prefix='/recordatorios', tags=['Recordatorios'])

@router.get('/', status_code=status.HTTP_200_OK)
def obtener_recordatorios_usuario(
    fecha: str = Query(),
    id_prospecto: Optional[int] = Query(None),
    usuario: Usuario = Depends(get_current_user),
    use_case: ObtenerRecordatoriosUsuarioUseCase = Depends(get_obtener_recordatorios_usuario_use_case)
):
    recordatorios = use_case.ejecutar(
        rut_usuario=usuario.rut,
        fecha=fecha,
        id_prospecto=id_prospecto
    )

    return {
        'recordatorios': recordatorios
    }


@router.post('/', status_code=status.HTTP_201_CREATED)
def registrar_recordatorio(
    request: RegistrarRecordatorioRequest,
    usuario: Usuario = Depends(get_current_user),
    use_case: RegistrarRecordatorioUseCase = Depends(get_registrar_recordatorio_use_case)
):
    use_case.ejecutar(
        rut_usuario=usuario.rut,
        titulo=request.titulo,
        detalle=request.detalle,
        prioridad=request.prioridad,
        tipo_gestion=request.tipo_gestion,
        fecha_recordatorio=request.fecha_recordatorio,
        id_prospecto=request.id_prospecto,
    )

    return {'message': 'Recordatorio creado correctamente'}


@router.get('/renovacion', status_code=status.HTTP_200_OK)
def obtener_recordatorios_renovacion(

):
    pass

    
@router.get('/cobranza', status_code=status.HTTP_200_OK)
def obtener_recordatorios_cobranza(

):
    pass