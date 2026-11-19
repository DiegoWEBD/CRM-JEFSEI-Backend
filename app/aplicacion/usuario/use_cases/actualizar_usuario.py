from uuid import UUID

from app.aplicacion.auth.authentication_service import AuthenticationService
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.dominio.rol.rol import Rol
from app.dominio.sucursal.sucursal import Sucursal
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.dominio.usuario.usuario import Usuario
from app.dominio.usuario.validar_password import validar_fortaleza_password


class ActualizarUsuarioUseCase:
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
        password: str | None,
        meta_mensual_uf: int | None,
        codigo_roles: list[str],
        porcentaje_comision: float | None,
        habilitado: bool,
        sesion_id_ejecutor: UUID | None = None
    ) -> bool:
        if not codigo_roles:
            raise ConflictoEnAccionException("Debe asignar al menos un rol")

        existente = self.repositorio_usuarios.buscar(rut)

        if not existente:
            raise RecursoNoEncontradoException("El usuario no existe")
        
        if correo and correo != existente.correo and self.repositorio_usuarios.existe_correo(correo):
            raise RecursoYaExisteException("El correo ya está en uso")
        
        if telefono and telefono != existente.telefono and self.repositorio_usuarios.existe_telefono(telefono):
            raise RecursoYaExisteException("El teléfono ya está en uso")

        if password:
            # Validación defensiva: también aplica si el caso de uso se invoca
            # fuera de la capa HTTP. Vacío/None mantiene la contraseña actual.
            validar_fortaleza_password(password)
            password_hash = self.authentication_service.hash_password(password)
        else:
            password_hash = existente.password_hash

        sucursal = Sucursal(id=id_sucursal, nombre='')
        roles = [Rol(codigo=codigo, nombre='') for codigo in codigo_roles]

        usuario = Usuario(
            rut=rut,
            nombre=nombre,
            correo=correo,
            telefono=telefono,
            sucursal=sucursal,
            password_hash=password_hash,
            roles=roles,
            meta_mensual_uf=meta_mensual_uf,
            habilitado=habilitado,
            eliminado=existente.eliminado,
            porcentaje_comision=porcentaje_comision,
        )

        if not self.repositorio_usuarios.actualizar(usuario):
            return False

        if not self.repositorio_usuarios.asignar_roles(rut, codigo_roles):
            return False

        if password:
            # Al cambiar la contraseña se revocan las sesiones del usuario
            # afectado para forzar un nuevo inicio de sesión. La sesión del
            # ejecutor se excluye por si un admin edita su propio usuario.
            self.authentication_service.revocar_todas_las_sesiones_excepto(
                rut, sesion_id_ejecutor, motivo='password_change',
            )

        return True
