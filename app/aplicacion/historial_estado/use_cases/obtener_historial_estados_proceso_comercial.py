from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.historial_estado.historial_estado import HistorialEstado
from app.dominio.historial_estado.repositorio_historial_estado import RepositorioHistorialEstado
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales


class ObtenerHistorialEstadosProcesoComercialUseCase:

    def __init__(
        self, 
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_historial_estado: RepositorioHistorialEstado
    ) -> None:
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.repositorio_historial_estado = repositorio_historial_estado

    def ejecutar(self, id_proceso_comercial: int) -> list[HistorialEstado]:

        if not self.repositorio_procesos_comerciales.buscar(id_proceso_comercial):
            raise RecursoNoEncontradoException('Proceso comercial no encontrado')
        
        return self.repositorio_historial_estado.buscar_historial_proceso_comercial(id_proceso_comercial)
