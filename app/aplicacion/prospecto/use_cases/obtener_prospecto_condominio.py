from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos


class ObtenerProspectoCondominioUseCase:
    def __init__(self, repositorio_prospectos: RepositorioProspectos):
        self.repositorio_prospectos = repositorio_prospectos

    def ejecutar(self, id: int) -> ProspectoCondominio:
        prospecto = self.repositorio_prospectos.buscar_prospecto_condominio(id)

        if prospecto is None or prospecto.id is None:
            raise ValueError('No se encontró el prospecto')

        return prospecto