from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.aplicacion.recordatorio.use_cases.obtener_recordatorios import ObtenerRecordatoriosUseCase
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.recordatorio.dependencias.deps import get_obtener_recordatorios_use_case
from app.presentacion.api.recordatorio.dto.requests.obtener_recordatorios_request import ObtenerRecordatoriosRequest


router = APIRouter(prefix='/recordatorios', tags=['Recordatorios'])

@router.get('/', status_code=status.HTTP_200_OK)
def obtener_recordatorios(
    fecha: str = Query(),
    id_prospecto: Optional[int] = Query(None),
    usuario: Usuario = Depends(get_current_user),
    use_case: ObtenerRecordatoriosUseCase = Depends(get_obtener_recordatorios_use_case)
):
    try:
        recordatorios = use_case.ejecutar(
            rut_usuario=usuario.rut,
            fecha=fecha,
            id_prospecto=id_prospecto
        )

        return {
            'recordatorios': recordatorios
        }

    except Exception as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )