import pytest
from unittest.mock import MagicMock

from app.aplicacion.notificacion.use_cases.obtener_oportunidades_en_riesgo import ObtenerOportunidadesEnRiesgoUseCase
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioProcesosComerciales)


@pytest.mark.unit
class TestObtenerOportunidadesEnRiesgo:

    def test_filtra_por_el_ejecutivo_autenticado(self, repositorio_mock):
        repositorio_mock.obtener_en_riesgo.return_value = ([], 0)
        uc = ObtenerOportunidadesEnRiesgoUseCase(repositorio_mock)

        uc.ejecutar_paginado(
            rut_usuario="11111111-1", pagina=1, tamano_pagina=15
        )

        repositorio_mock.obtener_en_riesgo.assert_called_once_with(
            rut_usuario="11111111-1", pagina=1, tamano_pagina=15
        )

    def test_retorna_datos_y_total(self, repositorio_mock):
        repositorio_mock.obtener_en_riesgo.return_value = (["reporte-1", "reporte-2"], 2)
        uc = ObtenerOportunidadesEnRiesgoUseCase(repositorio_mock)

        datos, total = uc.ejecutar_paginado(
            rut_usuario="11111111-1", pagina=1, tamano_pagina=15
        )

        assert datos == ["reporte-1", "reporte-2"]
        assert total == 2

    def test_lista_vacia(self, repositorio_mock):
        repositorio_mock.obtener_en_riesgo.return_value = ([], 0)
        uc = ObtenerOportunidadesEnRiesgoUseCase(repositorio_mock)

        datos, total = uc.ejecutar_paginado(
            rut_usuario="11111111-1", pagina=1, tamano_pagina=15
        )

        assert datos == []
        assert total == 0

    def test_pasa_paginacion_al_repositorio(self, repositorio_mock):
        repositorio_mock.obtener_en_riesgo.return_value = ([], 0)
        uc = ObtenerOportunidadesEnRiesgoUseCase(repositorio_mock)

        uc.ejecutar_paginado(
            rut_usuario="11111111-1", pagina=4, tamano_pagina=10
        )

        repositorio_mock.obtener_en_riesgo.assert_called_once_with(
            rut_usuario="11111111-1", pagina=4, tamano_pagina=10
        )
