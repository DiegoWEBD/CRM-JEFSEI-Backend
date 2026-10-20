from unittest.mock import MagicMock

import pytest

from app.aplicacion.solicitud_cotizacion.use_cases.obtener_unidades_alicuotas import (
    ObtenerUnidadesAlicuotasUseCase,
)
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.solicitud_cotizacion.repositorio_unidades_alicuotas import RepositorioUnidadesAlicuotas
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.unidad_alicuota import UnidadAlicuota


def _use_case(autorizado=True):
    repositorio = MagicMock(spec=RepositorioUnidadesAlicuotas)
    repositorio.listar_por_solicitud.return_value = [
        UnidadAlicuota(identificador_unidad='Depto 1', prorrateo=2.5, fila_origen=2),
    ]
    authorization = MagicMock()
    authorization.usuario_puede_ver_solicitud_cotizacion.return_value = autorizado
    repositorio_solicitudes = MagicMock()
    repositorio_solicitudes.buscar.return_value = MagicMock()
    return ObtenerUnidadesAlicuotasUseCase(repositorio_solicitudes, repositorio, authorization), repositorio


@pytest.mark.unit
class TestObtenerUnidadesAlicuotas:

    def test_devuelve_las_unidades(self):
        uc, repositorio = _use_case()

        unidades = uc.ejecutar(10, '1-9')

        assert len(unidades) == 1
        repositorio.listar_por_solicitud.assert_called_once_with(10)

    def test_acceso_global_no_consulta_autorizacion(self):
        uc, repositorio = _use_case(autorizado=False)

        unidades = uc.ejecutar(10, None)

        assert len(unidades) == 1

    def test_sin_permiso_sobre_la_solicitud_es_rechazado(self):
        uc, repositorio = _use_case(autorizado=False)

        with pytest.raises(UsuarioNoAutorizadoException):
            uc.ejecutar(10, '1-9')

        repositorio.listar_por_solicitud.assert_not_called()
