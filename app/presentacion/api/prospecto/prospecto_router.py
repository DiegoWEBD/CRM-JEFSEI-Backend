from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.aplicacion.prospecto.servicios.consulta_prospectos_service import ConsultaProspectosService
from app.presentacion.api.auth.dependencias.permisos_prospectos import permisos_prospectos
from app.presentacion.api.prospecto.deps import get_consulta_prospectos_service


router = APIRouter(prefix="/prospectos", tags=["Prospectos"])

@router.get("/", status_code=status.HTTP_200_OK)
def obtener_prospectos(
    rut_usuario: Optional[str] = Query(None),
    _ = Depends(permisos_prospectos()),
    consulta_prospectos_service: ConsultaProspectosService = Depends(get_consulta_prospectos_service)
):
    try:
        
        prospectos = consulta_prospectos_service.obtener_todos(rut_usuario)

        return {
            "data": prospectos
        }

    except Exception as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )