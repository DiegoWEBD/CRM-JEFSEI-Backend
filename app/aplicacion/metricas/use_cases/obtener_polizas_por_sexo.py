from app.aplicacion.metricas.dto.metricas_dashboard_dto import ItemCantidadDto


class ObtenerPolizasPorSexoUseCase:

    def ejecutar(self, year: int, mes: int) -> list[ItemCantidadDto]:
        # El repositorio todavía no calcula el desglose por sexo;
        # se devuelve vacío hasta implementar la consulta.
        return []
