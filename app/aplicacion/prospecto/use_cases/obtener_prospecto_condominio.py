from app.dominio.evaluacion_riesgo.repositorio_evaluaciones_riesgo import RepositorioEvaluacionesRiesgo
from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos


class ObtenerProspectoCondominioUseCase:
    def __init__(self, repositorio_prospectos: RepositorioProspectos, repositorio_evaluaciones_riesgo: RepositorioEvaluacionesRiesgo):
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_evaluaciones_riesgo = repositorio_evaluaciones_riesgo

    def ejecutar(self, id: int) -> ProspectoCondominio:
        prospecto = self.repositorio_prospectos.buscar_prospecto_condominio(id)

        if prospecto is None or prospecto.id is None:
            raise ValueError('No se encontró el prospecto')

        evaluacion = self.repositorio_evaluaciones_riesgo.buscar_evaluacion(prospecto.id)

        if evaluacion is not None:
            prospecto.evaluacion_riesgo = evaluacion

        return prospecto