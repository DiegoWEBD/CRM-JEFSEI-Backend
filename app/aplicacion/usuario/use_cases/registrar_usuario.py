from app.aplicacion.auth.authentication_service import AuthenticationService
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
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
        correo: str | None,
        telefono: str | None,
        id_sucursal: int,
        password: str,
        meta_mensual_uf: int | None,
        codigo_roles: list[str],
        porcentaje_comision: float | None,
    ) -> bool:
        if len(codigo_roles) == 0:
            raise ConflictoEnAccionException("Debe asignar al menos un rol")

        usuario = self.repositorio_usuarios.buscar(rut)

        if usuario:
            raise RecursoYaExisteException("El usuario ya existe")
        
        if correo and self.repositorio_usuarios.existe_correo(correo):
            raise RecursoYaExisteException("El correo ya está en uso")
        
        if telefono and self.repositorio_usuarios.existe_telefono(telefono):
            raise RecursoYaExisteException("El teléfono ya está en uso")
        
        password_hash = self.authentication_service.hash_password(password)
        
        sucursal = Sucursal(id=id_sucursal, nombre='')
        roles = [Rol(codigo=codigo, nombre='') for codigo in codigo_roles]

        nuevo_usuario = Usuario(
            rut=rut,
            nombre=nombre,
            correo=correo,
            telefono=telefono,
            sucursal=sucursal,
            password_hash=password_hash,
            roles=roles,
            meta_mensual_uf=meta_mensual_uf,
            habilitado=True,
            eliminado=False,
            porcentaje_comision=porcentaje_comision,
        )

        return self.repositorio_usuarios.registrar(nuevo_usuario)