from app.aplicacion.auth.authentication_service import AuthenticationService
from app.dominio.rol.rol import Rol
from app.dominio.sucursal.sucursal import Sucursal
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.dominio.usuario.usuario import Usuario


class RegistrarUsuarioUseCase:
    def __init__(self, repositorio_usuarios: RepositorioUsuarios, authentication_service: AuthenticationService):
        self.repositorio_usuarios = repositorio_usuarios
        self.authentication_service = authentication_service

    def ejecutar(
        self,
        rut: str,
        nombre: str,
        correo: str,
        telefono: str,
        id_sucursal: int,
        password: str,
        meta_mensual_uf: int,
        codigo_roles: list[str]
    ) -> bool:
        usuario = self.repositorio_usuarios.buscar(rut)

        if usuario:
            raise Exception("El usuario ya existe")
        
        password_hash = self.authentication_service.hash_password(password)
        
        sucursal = Sucursal(id=id_sucursal)
        roles = [Rol(codigo=codigo) for codigo in codigo_roles]
        meta = None if meta_mensual_uf == 0 else meta_mensual_uf

        nuevo_usuario = Usuario(
            rut=rut,
            nombre=nombre,
            correo=correo,
            telefono=telefono,
            sucursal=sucursal,
            password_hash=password_hash,
            roles=roles,
            meta_mensual_uf=meta
        )

        return self.repositorio_usuarios.registrar(nuevo_usuario)