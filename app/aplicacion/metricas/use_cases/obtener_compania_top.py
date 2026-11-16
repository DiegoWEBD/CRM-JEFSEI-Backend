from app.aplicacion.metricas.dto.metricas_dashboard_dto import CompaniaTopDto
from app.dominio.metricas.repositorio_metricas_dashboard import (
    RepositorioMetricasDashboard,
)


class ObtenerCompaniaTopUseCase:

    def __init__(
        self,
        repositorio: RepositorioMetricasDashboard,
    ):
        self.repositorio = repositorio

    def ejecutar(self, year: int, mes: int) -> CompaniaTopDto | None:
        por_compania_raw = self.repositorio.obtener_prima_por_compania(
            year, mes
        )

        if not por_compania_raw:
            return None

        top = por_compania_raw[0]
        return CompaniaTopDto(
            nombre=top["nombre"],
            prima_neta=float(top["valor"]),
        )
