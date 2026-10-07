from app.aplicacion.auth.authentication_service import AuthenticationService
from app.aplicacion.auth.dtos.refrescar_token_response_dto import RefrescarTokenResponseDTO
from app.core.config import settings
from app.dominio.auth.exceptions import RefreshTokenInvalidoError
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios


class RefrescarTokenUseCase:
    """Rota el refresh token y emite un nuevo access token.

    Misma lógica de claims que IniciarSesionUseCase: el access token se
    arma desde el usuario actualizado en la base de datos, así que siempre
    trae los claims completos (rut, nombre, roles y permisos).
    """

    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        authentication_service: AuthenticationService,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.authentication_service = authentication_service

    def execute(self, refresh_token_plano: str) -> RefrescarTokenResponseDTO:
        # 1. Validar y rotar la familia de refresh.
        #    Los errores de dominio (inválido/reusado) se propagan al router.
        sesion, nuevo_refresh = self.authentication_service.rotar_refresh_token(refresh_token_plano)

        # 2. Usuario actualizado: es la fuente de verdad de los claims
        usuario = self.repositorio_usuarios.buscar(sesion.rut_usuario)

        if usuario is None or not usuario.habilitado or usuario.eliminado:
            # La sesión era válida pero el usuario ya no puede operar:
            # se revoca para no dejar una familia de refresh viva.
            self.authentication_service.revocar_sesion(
                sesion.id,
                motivo='usuario_invalido_en_refresh',
            )
            raise RefreshTokenInvalidoError()

        # 3. Access token con los mismos claims que el login
        access_token = self.authentication_service.crear_access_token(
            usuario,
            sid=str(sesion.id),
        )

        return RefrescarTokenResponseDTO(
            access_token=access_token,
            refresh_token=nuevo_refresh,
            usuario=usuario,
            expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
