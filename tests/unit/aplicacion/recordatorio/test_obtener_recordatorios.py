import pytest
from unittest.mock import MagicMock

from app.aplicacion.recordatorio.use_cases.obtener_recordatorios import ObtenerRecordatoriosUsuarioUseCase
from app.dominio.recordatorio.repositorio_recordatorios import RepositorioRecordatorios
from tests.factories.recordatorio_factory import (
    crear_recordatorio_usuario_mock,
    crear_recordatorio_renovacion_mock,
    crear_recordatorio_cobranza_mock,
)


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioRecordatorios)


@pytest.mark.unit
class TestObtenerRecordatoriosUsuarioUseCasePaginado:

    def test_combina_los_3_tipos(self, repositorio_mock):
        repositorio_mock.obtener_recordatorios_usuario.return_value = (
            [crear_recordatorio_usuario_mock(id=1)],
            1,
        )
        repositorio_mock.obtener_recordatorios_renovacion.return_value = (
            [crear_recordatorio_renovacion_mock(id=2)],
            1,
        )
        repositorio_mock.obtener_recordatorios_cobranza.return_value = (
            [crear_recordatorio_cobranza_mock(id=3)],
            1,
        )

        uc = ObtenerRecordatoriosUsuarioUseCase(repositorio_mock)
        datos, total = uc.ejecutar_paginado(
            rut_usuario="11111111-1",
            fecha="2026-09-01",
            id_prospecto=None,
            pagina=1,
            tamano_pagina=15,
        )

        assert len(datos) == 3
        assert total == 3

    def test_retorna_total_suma_de_los_3_tipos(self, repositorio_mock):
        repositorio_mock.obtener_recordatorios_usuario.return_value = (
            [crear_recordatorio_usuario_mock(id=i) for i in range(1, 4)],
            3,
        )
        repositorio_mock.obtener_recordatorios_renovacion.return_value = (
            [crear_recordatorio_renovacion_mock(id=i) for i in range(4, 7)],
            3,
        )
        repositorio_mock.obtener_recordatorios_cobranza.return_value = (
            [crear_recordatorio_cobranza_mock(id=7)],
            1,
        )

        uc = ObtenerRecordatoriosUsuarioUseCase(repositorio_mock)
        datos, total = uc.ejecutar_paginado(
            rut_usuario="11111111-1",
            fecha="2026-09-01",
            id_prospecto=None,
            pagina=1,
            tamano_pagina=15,
        )

        assert total == 7
        assert len(datos) == 7

    def test_un_tipo_vacio_los_demas_siguen(self, repositorio_mock):
        repositorio_mock.obtener_recordatorios_usuario.return_value = ([], 0)
        repositorio_mock.obtener_recordatorios_renovacion.return_value = (
            [crear_recordatorio_renovacion_mock(id=1)],
            1,
        )
        repositorio_mock.obtener_recordatorios_cobranza.return_value = (
            [crear_recordatorio_cobranza_mock(id=2)],
            1,
        )

        uc = ObtenerRecordatoriosUsuarioUseCase(repositorio_mock)
        datos, total = uc.ejecutar_paginado(
            rut_usuario="11111111-1",
            fecha="2026-09-01",
            id_prospecto=None,
            pagina=1,
            tamano_pagina=15,
        )

        assert len(datos) == 2
        assert total == 2

    def test_todos_vacios_retorna_lista_vacia_y_cero(self, repositorio_mock):
        repositorio_mock.obtener_recordatorios_usuario.return_value = ([], 0)
        repositorio_mock.obtener_recordatorios_renovacion.return_value = ([], 0)
        repositorio_mock.obtener_recordatorios_cobranza.return_value = ([], 0)

        uc = ObtenerRecordatoriosUsuarioUseCase(repositorio_mock)
        datos, total = uc.ejecutar_paginado(
            rut_usuario="11111111-1",
            fecha="2026-09-01",
            id_prospecto=None,
            pagina=1,
            tamano_pagina=15,
        )

        assert datos == []
        assert total == 0

    def test_pasa_paginacion_al_repositorio(self, repositorio_mock):
        repositorio_mock.obtener_recordatorios_usuario.return_value = ([], 0)
        repositorio_mock.obtener_recordatorios_renovacion.return_value = ([], 0)
        repositorio_mock.obtener_recordatorios_cobranza.return_value = ([], 0)

        uc = ObtenerRecordatoriosUsuarioUseCase(repositorio_mock)
        uc.ejecutar_paginado(
            rut_usuario="11111111-1",
            fecha="2026-09-01",
            id_prospecto=None,
            pagina=2,
            tamano_pagina=10,
        )

        repositorio_mock.obtener_recordatorios_usuario.assert_called_once_with(
            rut_usuario="11111111-1",
            fecha="2026-09-01",
            id_prospecto=None,
            pagina=2,
            tamano_pagina=10,
        )
        repositorio_mock.obtener_recordatorios_renovacion.assert_called_once_with(
            rut_usuario="11111111-1",
            fecha="2026-09-01",
            id_prospecto=None,
            pagina=2,
            tamano_pagina=10,
        )
        repositorio_mock.obtener_recordatorios_cobranza.assert_called_once_with(
            rut_usuario="11111111-1",
            fecha="2026-09-01",
            id_prospecto=None,
            pagina=2,
            tamano_pagina=10,
        )
