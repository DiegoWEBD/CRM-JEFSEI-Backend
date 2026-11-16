from app.aplicacion.metricas.dto.metricas_dashboard_dto import PrimaNetaMensualDto
from app.aplicacion.metricas.periodo import etiqueta_mes, mes_anterior
from app.dominio.metricas.repositorio_metricas_dashboard import (
    RepositorioMetricasDashboard,
)


class ObtenerPrimaNetaMensualUseCase:

    def __init__(
        self,
        repositorio: RepositorioMetricasDashboard,
    ):
        self.repositorio = repositorio

    def ejecutar(self, year: int, mes: int) -> PrimaNetaMensualDto:
        mes_actual = self.repositorio.obtener_prima_neta_mes(year, mes)

        anio_ant, mes_ant = mes_anterior(year, mes)
        prima_mes_anterior = self.repositorio.obtener_prima_neta_mes(
            anio_ant, mes_ant
        )

        variacion = (
            round(
                (mes_actual - prima_mes_anterior)
                / prima_mes_anterior
                * 100,
                1,
            )
            if prima_mes_anterior > 0
            else 0.0
        )

        return PrimaNetaMensualDto(
            total_prima_neta=mes_actual,
            variacion_mes_anterior=variacion,
            mes_label=etiqueta_mes(year, mes),
        )
