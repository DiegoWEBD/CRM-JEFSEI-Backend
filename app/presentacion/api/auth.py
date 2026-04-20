from fastapi import APIRouter, Depends, HTTPException, status
from app.presentacion.schemas.auth import IniciarSesionRequest, TokenResponse
from app.aplicacion.auth.use_cases.iniciar_sesion import IniciarSesionUseCase
from app.presentacion.api.deps import obtener_caso_de_uso_iniciar_sesion

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(
    request: IniciarSesionRequest,
    use_case: IniciarSesionUseCase = Depends(obtener_caso_de_uso_iniciar_sesion)
):
    token = use_case.execute(
        email=request.rut,
        password=request.password
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    return TokenResponse(access_token=token)