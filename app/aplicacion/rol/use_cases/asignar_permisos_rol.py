from app.aplicacion.auditoria.dtos.contexto_peticion import ContextoPeticion
from app.aplicacion.auditoria.servicio_auditoria import ServicioAuditoria
from app.dominio.auditoria.eventos_auditoria import EventoAuditoria, ResultadoAuditoria
from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.permiso.repositorio_permisos import RepositorioPermisos
from app.dominio.rol.repositorio_roles import RepositorioRoles
from app.dominio.usuario.usuario import Usuario


class AsignarPermisosRolUseCase:

    def __init__(
        self,
        repositorio_roles: RepositorioRoles,
        repositorio_permisos: RepositorioPermisos,
        servicio_auditoria: ServicioAuditoria,
    ):
        self.repositorio_roles = repositorio_roles
        self.repositorio_permisos = repositorio_permisos
        self.servicio_auditoria = servicio_auditoria

    def ejecutar(
        self,
        codigo_rol: str,
        codigos_permiso: list[str],
        usuario_ejecutor: Usuario,
        contexto: ContextoPeticion,
    ) -> bool:
        rol = self.repositorio_roles.obtener_por_codigo(codigo_rol)

        if rol is None:
            raise RecursoNoEncontradoException('El rol no existe')

        codigos_unicos = list(dict.fromkeys(codigos_permiso))
        permisos = self.repositorio_permisos.obtener_por_codigos(codigos_unicos)
        codigos_encontrados = {permiso.codigo for permiso in permisos}
        faltantes = [
            codigo for codigo in codigos_unicos
            if codigo not in codigos_encontrados
        ]

        if faltantes:
            raise DatoInvalidoException(
                f'Permisos no válidos: {", ".join(faltantes)}'
            )

        if not self.repositorio_roles.asignar_permisos(codigo_rol, codigos_unicos):
            return False

        self.servicio_auditoria.registrar_accion_negocio(
            evento=EventoAuditoria.ACTUALIZAR,
            resultado=ResultadoAuditoria.EXITO,
            contexto=contexto,
            rut_usuario=usuario_ejecutor.rut,
            nombre_usuario=usuario_ejecutor.nombre,
            entidad_tipo='ROL',
            entidad_id=codigo_rol,
            detalle=(
                f'Permisos del rol {codigo_rol} actualizados: '
                f'{len(codigos_unicos)} permisos asignados'
            ),
        )

        return True
