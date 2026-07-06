from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.dominio.usuario.usuario import Usuario


class AsignarEjecutivoRenovacionUseCase:
    def __init__(
        self, 
        repositorio_prospectos: RepositorioProspectos,
        repositorio_usuarios: RepositorioUsuarios
    ):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_usuarios = repositorio_usuarios

    def ejecutar(self, id_cliente: int, rut_ej_renovacion: str | None, asignado_por: Usuario):
        prospecto = self.repositorio_prospectos.buscar_cliente(id_cliente)

        if not prospecto:
            raise RecursoNoEncontradoException('Cliente no encontrado')

        if rut_ej_renovacion is not None:
            usuario = self.repositorio_usuarios.buscar(rut_ej_renovacion)

            if not usuario:
                raise RecursoNoEncontradoException('Usuario no encontrado')

            prospecto.ejecutivo_renovacion_asignado = usuario
        else:
            prospecto.ejecutivo_renovacion_asignado = None

        self.repositorio_prospectos.asignar_ejecutivo_renovacion(prospecto, asignado_por)
