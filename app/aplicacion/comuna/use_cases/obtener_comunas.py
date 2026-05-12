from app.dominio.comuna.comuna import Comuna
from app.dominio.comuna.repositorio_comunas import RepositorioComunas


class ObtenerComunasUseCase:
    
    def __init__(self, repositorio_comunas: RepositorioComunas):
        self.repositorio_comunas = repositorio_comunas

    def ejecutar(self) -> list[Comuna]:
        return self.repositorio_comunas.obtener_todas()