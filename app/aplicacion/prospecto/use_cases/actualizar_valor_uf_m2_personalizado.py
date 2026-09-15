from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos


class ActualizarValorUfM2PersonalizadoUseCase:

    def __init__(self, repositorio_prospectos: RepositorioProspectos):
        self.repositorio_prospectos = repositorio_prospectos

    def ejecutar(self, id: int, valor_uf_m2_personalizado: float | None):
        prospecto = self.repositorio_prospectos.buscar_prospecto_condominio(id)

        if prospecto is None:
            raise RecursoNoEncontradoException('Prospecto no encontrado')

        prospecto.valor_uf_m2_personalizado = valor_uf_m2_personalizado
        self.repositorio_prospectos.actualizar_prospecto_condominio(prospecto)
