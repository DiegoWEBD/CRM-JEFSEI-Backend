from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.prospecto.use_cases.asignar_ejecutivo_comercial import (
    AsignarEjecutivoComercialUseCase,
)

MODULO = 'app.aplicacion.prospecto.use_cases.asignar_ejecutivo_comercial'


def _prospecto_mock(id=1, ejecutivo_previo=None):
    p = MagicMock()
    p.id = id
    p.nombre_riesgo = 'Prospecto Test'
    p.ejecutivo_comercial_asignado = ejecutivo_previo
    return p


def _use_case(prospecto, generar_alertas, rut_nuevo=None):
    repo_prospectos = MagicMock()
    repo_prospectos.buscar.return_value = prospecto
    repo_usuarios = MagicMock()
    if rut_nuevo is not None:
        repo_usuarios.buscar.return_value = MagicMock(rut=rut_nuevo)
    uc = AsignarEjecutivoComercialUseCase(repo_prospectos, repo_usuarios, generar_alertas)
    return uc, repo_prospectos


@pytest.mark.unit
@patch(f'{MODULO}.hub')
class TestAsignarEjecutivoComercialReevaluaAlertas:

    def test_acepta_el_caso_de_generacion_de_alertas_por_constructor(self, _mock_hub):
        generar = MagicMock()
        uc, _ = _use_case(_prospecto_mock(), generar, rut_nuevo='22222222-2')

        assert uc.generar_alertas_cierre is generar

    def test_re_evalua_alertas_cuando_cambia_el_rut(self, _mock_hub):
        prospecto = _prospecto_mock(ejecutivo_previo=MagicMock(rut='11111111-1'))
        generar = MagicMock()
        uc, repo_prospectos = _use_case(prospecto, generar, rut_nuevo='22222222-2')

        uc.ejecutar(id_prospecto=1, rut_ej_comercial='22222222-2', asignado_por=MagicMock())

        repo_prospectos.asignar_ejecutivo_comercial.assert_called_once()
        generar.ejecutar.assert_called_once()
        kwargs = generar.ejecutar.call_args.kwargs
        assert kwargs['id_prospecto'] == 1
        assert isinstance(kwargs['ahora'], datetime)
        assert kwargs['verificar_existencia'] is False

    def test_re_evalua_cuando_se_desasigna(self, _mock_hub):
        prospecto = _prospecto_mock(ejecutivo_previo=MagicMock(rut='11111111-1'))
        generar = MagicMock()
        uc, _ = _use_case(prospecto, generar, rut_nuevo=None)

        uc.ejecutar(id_prospecto=1, rut_ej_comercial=None, asignado_por=MagicMock())

        generar.ejecutar.assert_called_once()
        assert generar.ejecutar.call_args.kwargs['id_prospecto'] == 1
        assert generar.ejecutar.call_args.kwargs['verificar_existencia'] is False

    def test_no_re_evalua_si_el_rut_no_cambia(self, _mock_hub):
        prospecto = _prospecto_mock(ejecutivo_previo=MagicMock(rut='11111111-1'))
        generar = MagicMock()
        uc, repo_prospectos = _use_case(prospecto, generar, rut_nuevo='11111111-1')

        uc.ejecutar(id_prospecto=1, rut_ej_comercial='11111111-1', asignado_por=MagicMock())

        repo_prospectos.asignar_ejecutivo_comercial.assert_called_once()
        generar.ejecutar.assert_not_called()
