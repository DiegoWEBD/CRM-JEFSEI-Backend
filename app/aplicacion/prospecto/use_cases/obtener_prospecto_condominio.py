from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.historial_estado.repositorio_historial_estado import RepositorioHistorialEstado
from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos


class ObtenerProspectoCondominioUseCase:
    def __init__(
        self, 
        repositorio_prospectos: RepositorioProspectos
    ):
        self.repositorio_prospectos = repositorio_prospectos

    def ejecutar(self, id: int, rut_usuario: str | None) -> ProspectoCondominio:
        prospecto = self.repositorio_prospectos.buscar_prospecto_condominio(id, rut_usuario)

        if prospecto is None or prospecto.id is None:
            raise RecursoNoEncontradoException('No se encontró el prospecto')
        
        return prospecto