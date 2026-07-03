from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.dominio.usuario.usuario import Usuario


class AsignarEjecutivoEvaluacionUseCase:
    def __init__(self, repositorio_prospectos: RepositorioProspectos, repositorio_usuarios: RepositorioUsuarios):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_usuarios = repositorio_usuarios

    def ejecutar(self, id_prospecto: int, rut_ej_evaluacion: str | None, asignado_por: Usuario):
        prospecto = self.repositorio_prospectos.buscar(id_prospecto)

        if not prospecto:
            raise RecursoNoEncontradoException('Prospecto no encontrado')

        if rut_ej_evaluacion is not None:
            usuario = self.repositorio_usuarios.buscar(rut_ej_evaluacion)

            if not usuario:
                raise RecursoNoEncontradoException('Usuario no encontrado')

            prospecto.ejecutivo_evaluacion_asignado = usuario
        else:
            prospecto.ejecutivo_evaluacion_asignado = None

        self.repositorio_prospectos.asignar_ejecutivo_evaluacion_proyectos(prospecto, asignado_por)