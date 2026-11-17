import pytest
from unittest.mock import MagicMock

from app.aplicacion.metricas.use_cases.obtener_tendencia_anual import (
    ObtenerTendenciaAnualUseCase,
)
from app.dominio.metricas.repositorio_metricas_dashboard import (
    RepositorioMetricasDashboard,
)


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioMetricasDashboard)


class TestObtenerTendenciaAnualUseCase:

    def test_delega_year_y_mes_al_repositorio(self, repositorio_mock):
        repositorio_mock.obtener_tendencia_anual.return_value = []
        use_case = ObtenerTendenciaAnualUseCase(repositorio_mock)

        use_case.ejecutar(2026, 5)

        repositorio_mock.obtener_tendencia_anual.assert_called_once_with(
            2026, 5
        )

    def test_serie_cubre_enero_hasta_mes_seleccionado(self, repositorio_mock):
        repositorio_mock.obtener_tendencia_anual.return_value = []
        use_case = ObtenerTendenciaAnualUseCase(repositorio_mock)

        serie = use_case.ejecutar(2026, 5)

        assert [dto.mes for dto in serie] == [
            '2026-01', '2026-02', '2026-03', '2026-04', '2026-05',
        ]

    def test_meses_sin_produccion_quedan_en_cero(self, repositorio_mock):
        repositorio_mock.obtener_tendencia_anual.return_value = [
            {'mes': '2026-01', 'prima_neta': 100.0},
            {'mes': '2026-03', 'prima_neta': 50.0},
        ]
        use_case = ObtenerTendenciaAnualUseCase(repositorio_mock)

        serie = use_case.ejecutar(2026, 3)

        assert [(dto.mes, dto.prima_neta) for dto in serie] == [
            ('2026-01', 100.0),
            ('2026-02', 0.0),
            ('2026-03', 50.0),
        ]

    def test_ignora_meses_posteriores_y_de_otros_anios(
        self, repositorio_mock
    ):
        repositorio_mock.obtener_tendencia_anual.return_value = [
            {'mes': '2025-12', 'prima_neta': 999.0},
            {'mes': '2026-01', 'prima_neta': 100.0},
            {'mes': '2026-06', 'prima_neta': 888.0},
        ]
        use_case = ObtenerTendenciaAnualUseCase(repositorio_mock)

        serie = use_case.ejecutar(2026, 1)

        assert [(dto.mes, dto.prima_neta) for dto in serie] == [
            ('2026-01', 100.0),
        ]

    def test_enero_devuelve_un_solo_mes(self, repositorio_mock):
        repositorio_mock.obtener_tendencia_anual.return_value = []
        use_case = ObtenerTendenciaAnualUseCase(repositorio_mock)

        serie = use_case.ejecutar(2026, 1)

        assert [(dto.mes, dto.prima_neta) for dto in serie] == [
            ('2026-01', 0.0),
        ]

    def test_diciembre_cubre_todo_el_anio(self, repositorio_mock):
        repositorio_mock.obtener_tendencia_anual.return_value = []
        use_case = ObtenerTendenciaAnualUseCase(repositorio_mock)

        serie = use_case.ejecutar(2026, 12)

        assert len(serie) == 12
        assert serie[0].mes == '2026-01'
        assert serie[-1].mes == '2026-12'
