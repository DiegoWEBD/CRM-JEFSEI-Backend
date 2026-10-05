from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.dominio.usuario.usuario import Usuario


class AsignarAsistenteRenovacionUseCase:
    def __init__(
        self,
        repositorio_prospectos: RepositorioProspectos,
        repositorio_usuarios: RepositorioUsuarios
    ):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_usuarios = repositorio_usuarios

    def ejecutar(self, id_cliente: int, rut_as_renovacion: str | None, asignado_por: Usuario):
        prospecto = self.repositorio_prospectos.buscar_cliente(id_cliente)

        if not prospecto:
            raise RecursoNoEncontradoException('Cliente no encontrado')

        rut_anterior = prospecto.asistente_renovacion_asignado.rut if prospecto.asistente_renovacion_asignado else None

        if rut_as_renovacion is not None:
            usuario = self.repositorio_usuarios.buscar(rut_as_renovacion)

            if not usuario:
                raise RecursoNoEncontradoException('Usuario no encontrado')

            prospecto.asistente_renovacion_asignado = usuario
        else:
            prospecto.asistente_renovacion_asignado = None

        self.repositorio_prospectos.asignar_asistente_renovacion(prospecto, asignado_por)

        if rut_as_renovacion is not None:
            hub.publicar_desde_hilo(
                [rut_as_renovacion],
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'asignacion_ejecutivo'},
            )

        if rut_anterior and rut_anterior != rut_as_renovacion:
            hub.publicar_desde_hilo(
                [rut_anterior],
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'desasignacion_ejecutivo'},
            )
