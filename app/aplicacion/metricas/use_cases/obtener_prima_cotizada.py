from app.aplicacion.metricas.dto.metricas_dashboard_dto import PrimaCotizadaDto
from app.dominio.proyeccion.repositorio_proyecciones_comerciales import (
    RepositorioProyeccionesComerciales,
)


class ObtenerPrimaCotizadaUseCase:
    """Prima cotizada de las oportunidades abiertas.

    El cálculo lo hace `RepositorioProyeccionesComerciales` en SQL (solo
    cotizaciones vigentes), el mismo criterio que alimenta la vista de
    oportunidades.
    """

    def __init__(
        self,
        repositorio_proyecciones: RepositorioProyeccionesComerciales,
    ):
        self.repositorio_proyecciones = repositorio_proyecciones

    def ejecutar(self) -> PrimaCotizadaDto:
        return PrimaCotizadaDto(
            prima_cotizada=self.repositorio_proyecciones.prima_cotizada_total_abiertos()
        )
