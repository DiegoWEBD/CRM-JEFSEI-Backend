from unittest.mock import MagicMock

import pytest

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.proceso_comercial.use_cases.administrar_unidad_alicuota import (
    SIN_CAMBIO,
    AdministrarUnidadAlicuotaUseCase,
)
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.calculadora_desglose_reconstruccion import (
    CalculadoraDesgloseReconstruccion,
)
from app.dominio.unidades.repositorio_unidades_alicuotas import RepositorioUnidadesAlicuotas
from app.dominio.unidades.unidad_alicuota import UnidadAlicuota


def _proceso(cerrado=False, codigo_producto='unidades'):
    proceso = MagicMock()
    proceso.id = 42
    proceso.cerrado = cerrado
    proceso.producto.codigo = codigo_producto
    return proceso


def _unidad(**campos):
    datos = {'identificador_unidad': 'Depto 1', 'prorrateo': 0.030456521, 'fila_origen': 2, 'id': 7}
    datos.update(campos)
    return UnidadAlicuota(**datos)


def _use_case(unidad=None, autorizado=True, proceso=None):
    repositorio_procesos = MagicMock(spec=RepositorioProcesosComerciales)
    repositorio_procesos.buscar.return_value = proceso if proceso is not None else _proceso()

    repositorio_unidades = MagicMock(spec=RepositorioUnidadesAlicuotas)
    repositorio_unidades.buscar_por_id.return_value = unidad if unidad is not None else _unidad()

    authorization = MagicMock()
    authorization.usuario_puede_administrar_alicuotas.return_value = autorizado

    uc = AdministrarUnidadAlicuotaUseCase(
        repositorio_procesos,
        repositorio_unidades,
        authorization,
    )
    return uc, repositorio_unidades, authorization


@pytest.mark.unit
class TestAdministrarUnidadAlicuota:

    def test_descarta_la_unidad_sin_eliminarla(self):
        uc, repositorio_unidades, _ = _use_case()

        unidad = uc.ejecutar(42, 7, MagicMock(rut='1'), descartada=True)

        assert unidad.descartada is True
        repositorio_unidades.actualizar_unidad.assert_called_once_with(7, True, None)

    def test_restaura_la_unidad_descartada(self):
        uc, repositorio_unidades, _ = _use_case(unidad=_unidad(descartada=True))

        unidad = uc.ejecutar(42, 7, MagicMock(rut='1'), descartada=False)

        assert unidad.descartada is False
        repositorio_unidades.actualizar_unidad.assert_called_once_with(7, False, None)

    def test_fija_el_monto_asegurado_personalizado(self):
        uc, repositorio_unidades, _ = _use_case()

        unidad = uc.ejecutar(42, 7, MagicMock(rut='1'), monto_asegurado_personalizado=1500)

        assert unidad.monto_asegurado_personalizado == 1500.0
        repositorio_unidades.actualizar_unidad.assert_called_once_with(7, False, 1500.0)

    def test_monto_nulo_vuelve_al_monto_sugerido(self):
        uc, repositorio_unidades, _ = _use_case(unidad=_unidad(monto_asegurado_personalizado=1500.0))

        unidad = uc.ejecutar(42, 7, MagicMock(rut='1'), monto_asegurado_personalizado=None)

        assert unidad.monto_asegurado_personalizado is None
        repositorio_unidades.actualizar_unidad.assert_called_once_with(7, False, None)

    def test_los_campos_no_informados_no_se_modifican(self):
        uc, repositorio_unidades, _ = _use_case(unidad=_unidad(descartada=True, monto_asegurado_personalizado=900.0))

        unidad = uc.ejecutar(42, 7, MagicMock(rut='1'), descartada=SIN_CAMBIO, monto_asegurado_personalizado=SIN_CAMBIO)

        assert unidad.descartada is True
        assert unidad.monto_asegurado_personalizado == 900.0
        repositorio_unidades.actualizar_unidad.assert_called_once_with(7, True, 900.0)

    @pytest.mark.parametrize('monto', [0, -100, float('inf'), float('nan')])
    def test_monto_invalido_es_conflicto(self, monto):
        uc, repositorio_unidades, _ = _use_case()

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar(42, 7, MagicMock(rut='1'), monto_asegurado_personalizado=monto)

        repositorio_unidades.actualizar_unidad.assert_not_called()

    def test_unidad_de_otra_oportunidad_no_se_encuentra(self):
        uc, repositorio_unidades, _ = _use_case()
        repositorio_unidades.buscar_por_id.return_value = None

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar(42, 99, MagicMock(rut='1'), descartada=True)

        repositorio_unidades.actualizar_unidad.assert_not_called()

    def test_sin_permiso_es_rechazado(self):
        uc, repositorio_unidades, _ = _use_case(autorizado=False)

        with pytest.raises(UsuarioNoAutorizadoException):
            uc.ejecutar(42, 7, MagicMock(rut='1'), descartada=True)

        repositorio_unidades.actualizar_unidad.assert_not_called()

    def test_oportunidad_cerrada_es_conflicto(self):
        uc, _, _ = _use_case(proceso=_proceso(cerrado=True))

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar(42, 7, MagicMock(rut='1'), descartada=True)

    def test_oportunidad_que_no_es_de_unidades_es_conflicto(self):
        uc, _, _ = _use_case(proceso=_proceso(codigo_producto='espacios_comunes'))

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar(42, 7, MagicMock(rut='1'), descartada=True)

    def test_oportunidad_no_encontrada(self):
        uc, _, _ = _use_case(proceso=MagicMock(id=None))

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar(99, 7, MagicMock(rut='1'), descartada=True)


@pytest.mark.unit
class TestCalculadoraConConfiguracionPorUnidad:

    def test_monto_personalizado_reemplaza_al_sugerido(self):
        desglose = CalculadoraDesgloseReconstruccion.calcular(4760.0, [
            _unidad(monto_asegurado_personalizado=1500.0),
            _unidad(identificador_unidad='Depto 2', prorrateo=0.069543479, fila_origen=3),
        ])

        assert desglose[0].monto_asegurado_sugerido == 200.0
        assert desglose[0].monto_asegurado == 1500.0
        assert desglose[0].tiene_monto_asegurado_personalizado is True
        # 1.500 sobre el total (1.500 + 400)
        assert desglose[0].prorrateo_pago == pytest.approx(1500.0 / 1900.0)
        assert desglose[1].prorrateo_pago == pytest.approx(400.0 / 1900.0)
        assert CalculadoraDesgloseReconstruccion.total_monto_asegurado(desglose) == 1900.0
        assert CalculadoraDesgloseReconstruccion.total_monto_asegurado_sugerido(desglose) == 600.0

    def test_unidad_descartada_no_aporta_ni_paga(self):
        desglose = CalculadoraDesgloseReconstruccion.calcular(4760.0, [
            _unidad(descartada=True),
            _unidad(identificador_unidad='Depto 2', prorrateo=0.069543479, fila_origen=3),
        ])

        assert desglose[0].descartada is True
        assert desglose[0].prorrateo_pago == 0.0
        assert desglose[1].prorrateo_pago == 1.0
        assert CalculadoraDesgloseReconstruccion.total_monto_asegurado(desglose) == 400.0

    def test_todas_descartadas_no_reparte_pago(self):
        desglose = CalculadoraDesgloseReconstruccion.calcular(4760.0, [
            _unidad(descartada=True),
            _unidad(identificador_unidad='Depto 2', prorrateo=0.069543479, fila_origen=3, descartada=True),
        ])

        assert CalculadoraDesgloseReconstruccion.total_monto_asegurado(desglose) == 0.0
        assert [u.prorrateo_pago for u in desglose] == [0.0, 0.0]


@pytest.mark.unit
class TestUsuarioPuedeAdministrarAlicuotas:

    def _service(self, permiso=True, evaluacion_asignado='1-1'):
        repositorio_usuarios = MagicMock()
        repositorio_usuarios.usuario_tiene_permiso.return_value = permiso

        prospecto = MagicMock()
        prospecto.ejecutivo_evaluacion_asignado = (
            MagicMock(rut=evaluacion_asignado) if evaluacion_asignado is not None else None
        )

        repositorio_prospectos = MagicMock()
        repositorio_prospectos.buscar_prospecto_por_proceso_comercial.return_value = prospecto

        return AuthorizationService(MagicMock(), repositorio_prospectos, repositorio_usuarios)

    def test_evaluador_asignado_con_permiso_administra(self):
        assert self._service(permiso=True, evaluacion_asignado='1-1').usuario_puede_administrar_alicuotas(
            MagicMock(rut='1-1'), 42
        ) is True

    def test_otro_usuario_no_administra(self):
        assert self._service(permiso=True, evaluacion_asignado='1-1').usuario_puede_administrar_alicuotas(
            MagicMock(rut='2-2'), 42
        ) is False

    def test_sin_el_permiso_no_administra(self):
        assert self._service(permiso=False, evaluacion_asignado='1-1').usuario_puede_administrar_alicuotas(
            MagicMock(rut='1-1'), 42
        ) is False

    def test_sin_evaluador_asignado_nadie_administra(self):
        assert self._service(permiso=True, evaluacion_asignado=None).usuario_puede_administrar_alicuotas(
            MagicMock(rut='1-1'), 42
        ) is False
