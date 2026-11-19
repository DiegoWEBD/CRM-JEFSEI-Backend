from app.aplicacion.auditoria.dtos.contexto_peticion import ContextoPeticion
from app.aplicacion.auditoria.servicio_auditoria import ServicioAuditoria
from app.dominio.auditoria.eventos_auditoria import EventoAuditoria, ResultadoAuditoria
from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios

LONGITUD_MINIMA_NOMBRE = 2
LONGITUD_MAXIMA_NOMBRE = 120


class ActualizarPerfilUseCase:
    """Self-service: el usuario actualiza su propio nombre de perfil."""

    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        servicio_auditoria: ServicioAuditoria,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.servicio_auditoria = servicio_auditoria

    def ejecutar(
        self,
        rut: str,
        nombre: str,
        contexto: ContextoPeticion,
    ) -> bool:
        # Validación defensiva: también aplica si el caso de uso se invoca
        # fuera de la capa HTTP.
        nombre = (nombre or '').strip()
        if not (LONGITUD_MINIMA_NOMBRE <= len(nombre) <= LONGITUD_MAXIMA_NOMBRE):
            raise DatoInvalidoException(
                f'El nombre debe tener entre {LONGITUD_MINIMA_NOMBRE} '
                f'y {LONGITUD_MAXIMA_NOMBRE} caracteres'
            )

        existente = self.repositorio_usuarios.buscar(rut)

        if not existente or existente.eliminado:
            raise RecursoNoEncontradoException('El usuario no existe')

        if not self.repositorio_usuarios.actualizar_nombre(rut, nombre):
            return False

        self.servicio_auditoria.registrar_accion_negocio(
            evento=EventoAuditoria.ACTUALIZAR,
            resultado=ResultadoAuditoria.EXITO,
            contexto=contexto,
            rut_usuario=rut,
            nombre_usuario=nombre,
            entidad_tipo='USUARIO',
            entidad_id=rut,
            detalle=f'Actualizó su nombre de perfil: "{existente.nombre}" -> "{nombre}"',
        )

        return True
