from abc import ABC, abstractmethod

from app.dominio.proyeccion.agregado_proyeccion_proceso import AgregadoProyeccionProceso


class RepositorioProyeccionesComerciales(ABC):
    """Agregados de proyección comercial calculados en base de datos.

    Reemplazan el recorrido en memoria proceso → solicitudes → cotizaciones
    por consultas agregadas: una sola query por métrica. La semántica es la
    misma que definía `ServicioProyeccionesComerciales`: solo cotizaciones
    vigentes, prima potencial = promedio de las vigentes, prima esperada =
    potencial × probabilidad de cierre (del ejecutivo o del estado).
    """

    @abstractmethod
    def prima_cotizada_total_abiertos(self) -> float:
        """Suma de la prima cotizada de las oportunidades abiertas."""
        pass

    @abstractmethod
    def prima_potencial_estimada_total_abiertos(self) -> float:
        """Suma de la prima potencial estimada de las oportunidades abiertas."""
        pass

    @abstractmethod
    def prima_esperada_total_abiertos(self) -> float:
        """Suma de la prima esperada de las oportunidades abiertas.

        Las oportunidades sin probabilidad de cierre no aportan.
        """
        pass

    @abstractmethod
    def proyeccion_prima_esperada_por_mes_abiertos(self) -> list[dict]:
        """Prima esperada agrupada por mes de la fecha estimada de cierre.

        Solo meses con al menos una oportunidad aportante, en orden
        ascendente. Devuelve `{'mes': 'YYYY-MM', 'prima_esperada': float}`.
        """
        pass

    @abstractmethod
    def agregados_por_proceso(self, ids_proceso: list[int]) -> dict[int, AgregadoProyeccionProceso]:
        """Primas por proceso para los ids indicados (vista de oportunidades).

        Devuelve un registro por id solicitado; los ids inexistentes no
        aparecen en el resultado.
        """
        pass

    @abstractmethod
    def tasa_cierre_oportunidades(self) -> dict:
        """Tasa de cierre de oportunidades: ganadas / cerradas.

        Solo cuentan como cerradas las oportunidades con estado final
        `GANADO` o `PERDIDO` (las descartadas no). Devuelve
        `{'oportunidades_ganadas': int, 'oportunidades_cerradas': int}`.
        """
        pass
