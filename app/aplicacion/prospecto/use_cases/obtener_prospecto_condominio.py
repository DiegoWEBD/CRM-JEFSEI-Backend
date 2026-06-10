from app.dominio.historial_estado.repositorio_historial_estado import RepositorioHistorialEstado
from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos


class ObtenerProspectoCondominioUseCase:
    def __init__(
        self, 
        repositorio_prospectos: RepositorioProspectos,
        repositorio_historial_estado: RepositorioHistorialEstado
    ):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_historial_estado = repositorio_historial_estado

    def ejecutar(self, id: int, rut_usuario: str | None) -> ProspectoCondominio:
        prospecto = self.repositorio_prospectos.buscar_prospecto_condominio(id, rut_usuario)

        if prospecto is None or prospecto.id is None:
            raise ValueError('No se encontró el prospecto')

        #historial_estados = self.repositorio_historial_estado.buscar_historial_prospecto(prospecto.id)
        #prospecto.proceso_comercial.historial_estados = historial_estados
        
        return prospecto