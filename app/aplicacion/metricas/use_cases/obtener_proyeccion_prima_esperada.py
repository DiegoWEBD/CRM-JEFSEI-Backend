from app.aplicacion.metricas.dto.metricas_dashboard_dto import (
    ProyeccionPrimaEsperadaDto,
)
from app.dominio.proyeccion.repositorio_proyecciones_comerciales import (
    RepositorioProyeccionesComerciales,
)


class ObtenerProyeccionPrimaEsperadaUseCase:
    """Proyección de prima esperada por mes de cierre estimado.

    El cálculo lo hace `RepositorioProyeccionesComerciales` en SQL, el
    mismo criterio que alimenta la vista de oportunidades.
    """

    def __init__(
        self,
        repositorio_proyecciones: RepositorioProyeccionesComerciales,
    ):
        self.repositorio_proyecciones = repositorio_proyecciones

    def ejecutar(self) -> list[ProyeccionPrimaEsperadaDto]:
        proyeccion = (
            self.repositorio_proyecciones.proyeccion_prima_esperada_por_mes_abiertos()
        )

        return [
            ProyeccionPrimaEsperadaDto(
                mes=item['mes'],
                prima_esperada=item['prima_esperada'],
            )
            for item in proyeccion
        ]
