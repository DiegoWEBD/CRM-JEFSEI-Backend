from fastapi import APIRouter, Depends, HTTPException, status
from app.infraestructura.usuario.adaptadores.usuario_json_adapter import UsuarioJsonAdapter
from app.presentacion.api.auth.schemas.auth import IniciarSesionRequest, TokenResponse
from app.aplicacion.auth.use_cases.iniciar_sesion import IniciarSesionUseCase
from app.presentacion.api.auth.dependencias.get_iniciar_sesion_use_case import get_iniciar_sesion_use_case

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(
    request: IniciarSesionRequest,
    use_case: IniciarSesionUseCase = Depends(get_iniciar_sesion_use_case)
):
    response = use_case.execute(
        rut=request.rut,
        password=request.password
    )

    if not response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    return TokenResponse(
        access_token=response.access_token,
        token_type='bearer',
        usuario=UsuarioJsonAdapter.Adapt(response.usuario)
    )