import pytest
from unittest.mock import MagicMock

from app.aplicacion.notificacion.use_cases.obtener_contador_no_leidas import ObtenerContadorNoLeidasUseCase
from app.aplicacion.notificacion.use_cases.obtener_notificaciones import ObtenerNotificacionesUseCase
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from tests.factories.notificacion_factory import crear_notificacion_mock


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioNotificaciones)


@pytest.mark.unit
class TestObtenerNotificaciones:

    def test_retorna_pagina_y_total(self, repositorio_mock):
        repositorio_mock.obtener_paginado.return_value = (
            [crear_notificacion_mock(id=1), crear_notificacion_mock(id=2)],
            2,
        )
        uc = ObtenerNotificacionesUseCase(repositorio_mock)

        datos, total = uc.ejecutar_paginado(
            rut_usuario="12345678-9",
            pagina=1,
            tamano_pagina=15,
            no_leidas=None,
            nivel=None,
            codigo_tipo=None,
        )

        assert len(datos) == 2
        assert total == 2

    def test_lista_vacia_retorna_total_cero(self, repositorio_mock):
        repositorio_mock.obtener_paginado.return_value = ([], 0)
        uc = ObtenerNotificacionesUseCase(repositorio_mock)

        datos, total = uc.ejecutar_paginado(
            rut_usuario="12345678-9",
            pagina=1,
            tamano_pagina=15,
            no_leidas=None,
            nivel=None,
            codigo_tipo=None,
        )

        assert datos == []
        assert total == 0

    def test_pasa_filtros_y_paginacion_al_repositorio(self, repositorio_mock):
        repositorio_mock.obtener_paginado.return_value = ([], 0)
        uc = ObtenerNotificacionesUseCase(repositorio_mock)

        uc.ejecutar_paginado(
            rut_usuario="11111111-1",
            pagina=3,
            tamano_pagina=10,
            no_leidas=True,
            nivel="CRITICO",
            codigo_tipo="SLA_VENCIDO",
        )

        repositorio_mock.obtener_paginado.assert_called_once_with(
            rut_usuario="11111111-1",
            no_leidas=True,
            nivel="CRITICO",
            codigo_tipo="SLA_VENCIDO",
            pagina=3,
            tamano_pagina=10,
        )

    def test_pagina_2_offset_al_repositorio(self, repositorio_mock):
        repositorio_mock.obtener_paginado.return_value = ([], 0)
        uc = ObtenerNotificacionesUseCase(repositorio_mock)

        uc.ejecutar_paginado(
            rut_usuario="12345678-9",
            pagina=2,
            tamano_pagina=15,
            no_leidas=None,
            nivel=None,
            codigo_tipo=None,
        )

        assert repositorio_mock.obtener_paginado.call_args.kwargs["pagina"] == 2


@pytest.mark.unit
class TestObtenerContadorNoLeidas:

    def test_retorna_contador_del_repositorio(self, repositorio_mock):
        repositorio_mock.obtener_contador_no_leidas.return_value = 7
        uc = ObtenerContadorNoLeidasUseCase(repositorio_mock)

        assert uc.ejecutar(rut_usuario="12345678-9") == 7
        repositorio_mock.obtener_contador_no_leidas.assert_called_once_with(
            rut_usuario="12345678-9"
        )

    def test_sin_no_leidas_retorna_cero(self, repositorio_mock):
        repositorio_mock.obtener_contador_no_leidas.return_value = 0
        uc = ObtenerContadorNoLeidasUseCase(repositorio_mock)

        assert uc.ejecutar(rut_usuario="12345678-9") == 0
