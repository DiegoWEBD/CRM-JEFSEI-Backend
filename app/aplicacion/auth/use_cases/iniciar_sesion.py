from app.aplicacion.auth.authentication_service import AuthenticationService
from app.aplicacion.auth.dtos.iniciar_sesion_response_dto import IniciarSesionResponseDTO
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.core.config import settings
    
class IniciarSesionUseCase:

    def __init__(self, repositorio_usuarios: RepositorioUsuarios, authentication_service: AuthenticationService):
        self.repositorio_usuarios = repositorio_usuarios
        self.authentication_service = authentication_service

    def execute(self, rut: str, password: str) -> IniciarSesionResponseDTO | None:
        usuario = self.repositorio_usuarios.buscar(rut)

        if not usuario:
            return None
        
        if not usuario.password_hash:
            return None

        if not usuario.habilitado or usuario.eliminado:
            return None

        if not self.authentication_service.verificar_password(password, usuario.password_hash):
            return None

        token = self.authentication_service.crear_access_token({
            "rut": usuario.rut,
            "nombre": usuario.nombre,
            "codigo_roles": [rol.codigo for rol in usuario.roles],
            "nombre_roles": [rol.nombre for rol in usuario.roles]
        })

        return IniciarSesionResponseDTO(
            access_token=token,
            usuario=usuario,
            expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )