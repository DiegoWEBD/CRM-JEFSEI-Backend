from app.aplicacion.metricas.dto.metricas_dashboard_dto import TasaCierreDto
from app.dominio.proyeccion.repositorio_proyecciones_comerciales import (
    RepositorioProyeccionesComerciales,
)


class ObtenerTasaCierreUseCase:
    """Tasa de cierre de oportunidades: ganadas / cerradas.

    Solo cuentan como cerradas las oportunidades con estado final
    `GANADO` o `PERDIDO` (las descartadas no). El conteo lo hace
    `RepositorioProyeccionesComerciales` en SQL.
    """

    def __init__(
        self,
        repositorio_proyecciones: RepositorioProyeccionesComerciales,
    ):
        self.repositorio_proyecciones = repositorio_proyecciones

    def ejecutar(self) -> TasaCierreDto:
        conteos = self.repositorio_proyecciones.tasa_cierre_oportunidades()
        ganadas = conteos['oportunidades_ganadas']
        cerradas = conteos['oportunidades_cerradas']
        tasa_cierre_pct = round(ganadas * 100.0 / cerradas, 2) if cerradas > 0 else 0.0
        return TasaCierreDto(
            tasa_cierre_pct=tasa_cierre_pct,
            oportunidades_ganadas=ganadas,
            oportunidades_cerradas=cerradas,
        )
