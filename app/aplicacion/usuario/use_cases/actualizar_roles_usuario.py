from app.aplicacion.auditoria.dtos.contexto_peticion import ContextoPeticion
from app.aplicacion.auditoria.servicio_auditoria import ServicioAuditoria
from app.dominio.auditoria.eventos_auditoria import EventoAuditoria, ResultadoAuditoria
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.rol.repositorio_roles import RepositorioRoles
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.dominio.usuario.usuario import Usuario


class ActualizarRolesUsuarioUseCase:

    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_roles: RepositorioRoles,
        servicio_auditoria: ServicioAuditoria,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_roles = repositorio_roles
        self.servicio_auditoria = servicio_auditoria

    def ejecutar(
        self,
        rut: str,
        codigo_roles: list[str],
        usuario_ejecutor: Usuario,
        contexto: ContextoPeticion,
    ) -> bool:
        if not codigo_roles:
            raise ConflictoEnAccionException('Debe asignar al menos un rol')

        existente = self.repositorio_usuarios.buscar(rut)

        if not existente or existente.eliminado:
            raise RecursoNoEncontradoException('El usuario no existe')

        codigos_unicos = list(dict.fromkeys(codigo_roles))
        codigos_validos = {
            rol.codigo for rol in self.repositorio_roles.obtener_todos()
        }
        faltantes = [
            codigo for codigo in codigos_unicos
            if codigo not in codigos_validos
        ]

        if faltantes:
            raise DatoInvalidoException(
                f'Roles no válidos: {", ".join(faltantes)}'
            )

        if not self.repositorio_usuarios.asignar_roles(rut, codigos_unicos):
            return False

        self.servicio_auditoria.registrar_accion_negocio(
            evento=EventoAuditoria.ACTUALIZAR,
            resultado=ResultadoAuditoria.EXITO,
            contexto=contexto,
            rut_usuario=usuario_ejecutor.rut,
            nombre_usuario=usuario_ejecutor.nombre,
            entidad_tipo='USUARIO',
            entidad_id=rut,
            detalle=(
                f'Roles del usuario {rut} actualizados: '
                f'{", ".join(codigos_unicos)}'
            ),
        )

        return True
