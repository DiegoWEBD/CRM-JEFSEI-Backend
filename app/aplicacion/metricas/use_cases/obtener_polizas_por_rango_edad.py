from app.aplicacion.metricas.dto.metricas_dashboard_dto import ItemCantidadDto


class ObtenerPolizasPorRangoEdadUseCase:

    def ejecutar(self, year: int, mes: int) -> list[ItemCantidadDto]:
        # El repositorio todavía no calcula el desglose por rango de edad;
        # se devuelve vacío hasta implementar la consulta.
        return []
