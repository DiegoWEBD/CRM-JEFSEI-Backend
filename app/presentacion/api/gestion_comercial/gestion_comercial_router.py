from fastapi import APIRouter, Depends, Query, status

from app.aplicacion.gestion_comercial.use_cases.obtener_gestiones_comerciales import ObtenerGestionesComercialesUseCase
from app.aplicacion.gestion_comercial.use_cases.obtener_ultima_gestion_comercial import ObtenerUltimaGestionComercialUseCase
from app.aplicacion.gestion_comercial.use_cases.registrar_gestion_comercial import RegistrarGestionComercialUseCase
from app.dominio.usuario.usuario import Usuario
from app.infraestructura.gestion_comercial.adaptadores.gestion_comercial_json_adapter import GestionComercialJsonAdapter
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.gestion_comercial.dependencias.deps import (
    get_obtener_gestiones_comerciales_use_case,
    get_obtener_ultima_gestion_comercial_use_case,
    get_registrar_gestion_comercial_use_case,
)
from app.presentacion.api.gestion_comercial.dto.gestion_comercial_json import GestionComercialJson
from app.presentacion.api.gestion_comercial.dto.requests.registrar_gestion_comercial_request import (
    RegistrarGestionComercialRequest,
)

router = APIRouter(prefix='/gestiones-comerciales', tags=['GestionesComerciales'])


@router.post('/', status_code=status.HTTP_201_CREATED)
def registrar_gestion_comercial(
    request: RegistrarGestionComercialRequest,
    usuario: Usuario = Depends(get_current_user),
    use_case: RegistrarGestionComercialUseCase = Depends(get_registrar_gestion_comercial_use_case),
) -> GestionComercialJson:
    gestion = use_case.ejecutar(
        tipo=request.tipo,
        rut_usuario=usuario.rut,
        id_prospecto=request.id_prospecto,
        titulo=request.titulo,
        estado_contacto=request.estado_contacto,
        observacion=request.observacion,
        fecha_gestion=request.fecha_gestion,
    )
    return GestionComercialJsonAdapter(gestion).to_json()


@router.get('/', status_code=status.HTTP_200_OK)
def obtener_gestiones_comerciales(
    id_prospecto: int | None = Query(None),
    use_case: ObtenerGestionesComercialesUseCase = Depends(get_obtener_gestiones_comerciales_use_case),
) -> dict[str, list[GestionComercialJson]]:
    gestiones = use_case.ejecutar(id_prospecto=id_prospecto)
    return {
        'gestiones': [GestionComercialJsonAdapter(g).to_json() for g in gestiones],
    }


@router.get('/final', status_code=status.HTTP_200_OK)
def obtener_ultima_gestion_comercial(
    id_prospecto: int = Query(...),
    use_case: ObtenerUltimaGestionComercialUseCase = Depends(get_obtener_ultima_gestion_comercial_use_case),
) -> GestionComercialJson | None:
    gestion = use_case.ejecutar(id_prospecto=id_prospecto)
    if gestion is None:
        return None
    return GestionComercialJsonAdapter(gestion).to_json()
