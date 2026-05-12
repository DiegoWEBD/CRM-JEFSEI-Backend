from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos


class ObtenerProspectoUseCase:
    def __init__(self, repositorio_prospectos: RepositorioProspectos):
        self.repositorio_prospectos = repositorio_prospectos

    def ejecutar(self, id: int) -> Prospecto:
        prospecto = self.repositorio_prospectos.buscar(id)
        print(prospecto)
        if prospecto is None:
            raise ValueError("No se encontró el prospecto")

        return prospecto