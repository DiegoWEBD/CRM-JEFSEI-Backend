from app.dominio.administrador_condominio.repositorio_administradores import RepositorioAdministradores
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.usuario import Usuario


class AsignarAdministradorCondominioUseCase:
    
    def __init__(
        self,
        repositorio_prospectos: RepositorioProspectos,
        repositorio_administradores: RepositorioAdministradores
    ) -> None:
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_administradores = repositorio_administradores

    def ejecutar(self, id_prospecto: int, id_administrador: int, usuario: Usuario):
        pass