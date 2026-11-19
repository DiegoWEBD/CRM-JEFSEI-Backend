from uuid import UUID

from app.aplicacion.auditoria.dtos.contexto_peticion import ContextoPeticion
from app.aplicacion.auditoria.servicio_auditoria import ServicioAuditoria
from app.aplicacion.auth.authentication_service import AuthenticationService
from app.dominio.auditoria.eventos_auditoria import ResultadoAuditoria
from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.dominio.usuario.validar_password import validar_fortaleza_password

EVENTO_CAMBIO_CONTRASENA = 'CAMBIO_PASSWORD'


class CambiarPasswordUseCase:
    """Self-service: el usuario cambia su propia contraseña.

    Exige la contraseña actual y, al cambiarla, revoca las demás sesiones
    del usuario (la sesión desde la que se hizo el cambio sigue viva).
    """

    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        authentication_service: AuthenticationService,
        servicio_auditoria: ServicioAuditoria,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.authentication_service = authentication_service
        self.servicio_auditoria = servicio_auditoria

    def ejecutar(
        self,
        rut: str,
        password_actual: str,
        password_nueva: str,
        sesion_id_actual: UUID | None,
        contexto: ContextoPeticion,
    ) -> bool:
        usuario = self.repositorio_usuarios.buscar(rut)

        if not usuario or usuario.eliminado:
            raise RecursoNoEncontradoException('El usuario no existe')

        password_actual_valida = (
            usuario.password_hash is not None
            and self.authentication_service.verificar_password(
                password_actual, usuario.password_hash
            )
        )
        if not password_actual_valida:
            raise DatoInvalidoException('La contraseña actual no es correcta')

        if password_actual == password_nueva:
            raise DatoInvalidoException(
                'La nueva contraseña no puede ser igual a la actual'
            )

        # Validación defensiva: también aplica si el caso de uso se invoca
        # fuera de la capa HTTP.
        validar_fortaleza_password(password_nueva)

        password_hash = self.authentication_service.hash_password(password_nueva)

        if not self.repositorio_usuarios.actualizar_password_hash(rut, password_hash):
            return False

        self.authentication_service.revocar_todas_las_sesiones_excepto(
            rut, sesion_id_actual, motivo='password_change',
        )

        self.servicio_auditoria.registrar_autenticacion(
            evento=EVENTO_CAMBIO_CONTRASENA,
            resultado=ResultadoAuditoria.EXITO,
            contexto=contexto,
            rut_usuario=rut,
            nombre_usuario=usuario.nombre,
            detalle=(
                'Cambió su contraseña; se revocaron sus demás sesiones activas'
            ),
        )

        return True
