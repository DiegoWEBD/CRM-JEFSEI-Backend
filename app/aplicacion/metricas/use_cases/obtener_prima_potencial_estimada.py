from app.aplicacion.metricas.dto.metricas_dashboard_dto import (
    PrimaPotencialEstimadaDto,
)
from app.dominio.proyeccion.repositorio_proyecciones_comerciales import (
    RepositorioProyeccionesComerciales,
)


class ObtenerPrimaPotencialEstimadaUseCase:
    """Prima potencial estimada de las oportunidades abiertas.

    El cálculo lo hace `RepositorioProyeccionesComerciales` en SQL, el
    mismo criterio que alimenta la vista de oportunidades.
    """

    def __init__(
        self,
        repositorio_proyecciones: RepositorioProyeccionesComerciales,
    ):
        self.repositorio_proyecciones = repositorio_proyecciones

    def ejecutar(self) -> PrimaPotencialEstimadaDto:
        return PrimaPotencialEstimadaDto(
            prima_potencial_estimada=(
                self.repositorio_proyecciones.prima_potencial_estimada_total_abiertos()
            )
        )
