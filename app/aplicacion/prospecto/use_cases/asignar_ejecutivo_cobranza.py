from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.dominio.usuario.usuario import Usuario


class AsignarEjecutivoCobranzaUseCase:
    def __init__(
        self, 
        repositorio_prospectos: RepositorioProspectos,
        repositorio_usuarios: RepositorioUsuarios
    ):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_usuarios = repositorio_usuarios

    def ejecutar(self, id_prospecto: int, rut_ej_comercial: str, asignado_por: Usuario):
        prospecto = self.repositorio_prospectos.buscar(id_prospecto)

        if not prospecto:
            raise RecursoNoEncontradoException('Prospecto no encontrado')
        
        usuario = self.repositorio_usuarios.buscar(rut_ej_comercial)

        if not usuario:
            raise RecursoNoEncontradoException('Usuario no encontrado')

        prospecto.ejecutivo_comercial_asignado = usuario
        self.repositorio_prospectos.asignar_ejecutivo_comercial(prospecto, asignado_por)