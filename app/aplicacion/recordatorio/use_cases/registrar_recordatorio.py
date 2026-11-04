from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.recordatorio.repositorio_recordatorios import RepositorioRecordatorios
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios


class RegistrarRecordatorioUseCase:

    def __init__(
        self,
        repositorio_recordatorios: RepositorioRecordatorios,
        repositorio_prospectos: RepositorioProspectos,
        repositorio_usuarios: RepositorioUsuarios,
    ):
        self.repositorio_recordatorios = repositorio_recordatorios
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_usuarios = repositorio_usuarios

    def ejecutar(
        self,
        rut_usuario: str,
        rut_usuario_destino: str | None,
        titulo: str,
        detalle: str | None,
        prioridad: str,
        tipo_gestion: str,
        fecha_recordatorio: str,
        id_prospecto: int | None,
    ) -> None:
        if rut_usuario_destino is not None:
            usuario = self.repositorio_usuarios.buscar(rut_usuario)
            if usuario is None or not self.repositorio_usuarios.usuario_tiene_permiso(
                usuario, 'CREAR_RECORDATORIO_GLOBAL'
            ):
                raise UsuarioNoAutorizadoException

            if self.repositorio_usuarios.buscar(rut_usuario_destino) is None:
                raise RecursoNoEncontradoException(
                    f'El usuario con RUT {rut_usuario_destino} no existe'
                )

        if id_prospecto is not None:
            prospecto = self.repositorio_prospectos.buscar(id_prospecto)
            if prospecto is None:
                raise RecursoNoEncontradoException(
                    f'El prospecto con id {id_prospecto} no existe'
                )

        self.repositorio_recordatorios.registrar(
            rut_usuario=rut_usuario_destino if rut_usuario_destino is not None else rut_usuario,
            titulo=titulo,
            detalle=detalle,
            prioridad=prioridad,
            tipo_gestion=tipo_gestion,
            fecha_recordatorio=fecha_recordatorio,
            id_prospecto=id_prospecto,
        )
