from app.aplicacion.auth.authentication_service import AuthenticationService
from app.aplicacion.auth.dtos.iniciar_sesion_response_dto import IniciarSesionResponseDTO
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
    
class IniciarSesionUseCase:

    def __init__(self, repositorio_usuarios: RepositorioUsuarios, authentication_service: AuthenticationService):
        self.repositorio_usuarios = repositorio_usuarios
        self.authentication_service = authentication_service

    def execute(self, rut: str, password: str) -> IniciarSesionResponseDTO | None:
        usuario = self.repositorio_usuarios.buscar(rut)

        if not usuario:
            return None

        if not self.authentication_service.verificar_password(password, usuario.password_hash):
            return None

        token = self.authentication_service.crear_access_token({"sub": str(usuario.rut)})

        return IniciarSesionResponseDTO(
            access_token=token,
            usuario=usuario
        )