from app.aplicacion.metricas.dto.metricas_dashboard_dto import PrimaEsperadaDto
from app.dominio.proyeccion.repositorio_proyecciones_comerciales import (
    RepositorioProyeccionesComerciales,
)


class ObtenerPrimaEsperadaUseCase:
    """Prima esperada de las oportunidades abiertas.

    El cálculo lo hace `RepositorioProyeccionesComerciales` en SQL, el
    mismo criterio que alimenta la vista de oportunidades. Las
    oportunidades sin probabilidad de cierre no aportan.
    """

    def __init__(
        self,
        repositorio_proyecciones: RepositorioProyeccionesComerciales,
    ):
        self.repositorio_proyecciones = repositorio_proyecciones

    def ejecutar(self) -> PrimaEsperadaDto:
        return PrimaEsperadaDto(
            prima_esperada=self.repositorio_proyecciones.prima_esperada_total_abiertos()
        )
