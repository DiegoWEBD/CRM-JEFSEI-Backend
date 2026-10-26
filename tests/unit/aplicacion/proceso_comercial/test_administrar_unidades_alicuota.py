from unittest.mock import MagicMock

import pytest

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.proceso_comercial.use_cases.administrar_unidades_alicuota import (
    SIN_CAMBIO,
    AdministrarUnidadesAlicuotaUseCase,
    CambioUnidadAlicuota,
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


def _unidades():
    return [
        _unidad(),
        _unidad(id=8, identificador_unidad='Depto 2', prorrateo=0.069543479, fila_origen=3),
        _unidad(id=9, identificador_unidad='Depto 3', prorrateo=0.05, fila_origen=4),
    ]


def _use_case(unidades=None, autorizado=True, proceso=None):
    repositorio_procesos = MagicMock(spec=RepositorioProcesosComerciales)
    repositorio_procesos.buscar.return_value = proceso if proceso is not None else _proceso()

    repositorio_unidades = MagicMock(spec=RepositorioUnidadesAlicuotas)
    repositorio_unidades.listar_por_oportunidad.return_value = (
        unidades if unidades is not None else _unidades()
    )

    authorization = MagicMock()
    authorization.usuario_puede_administrar_alicuotas.return_value = autorizado

    uc = AdministrarUnidadesAlicuotaUseCase(
        repositorio_procesos,
        repositorio_unidades,
        authorization,
    )
    return uc, repositorio_unidades, authorization


def _unidades_persistidas(repositorio_unidades):
    (unidades,), _ = repositorio_unidades.actualizar_unidades.call_args
    return {unidad.id: unidad for unidad in unidades}


@pytest.mark.unit
class TestAdministrarUnidadesAlicuota:

    def test_descarta_varias_unidades_en_un_solo_guardado(self):
        uc, repositorio_unidades, _ = _use_case()

        actualizadas = uc.ejecutar(
            42,
            [
                CambioUnidadAlicuota(7, descartada=True),
                CambioUnidadAlicuota(8, descartada=True),
            ],
            MagicMock(rut='1'),
        )

        assert [unidad.id for unidad in actualizadas] == [7, 8]
        assert all(unidad.descartada is True for unidad in actualizadas)
        repositorio_unidades.actualizar_unidades.assert_called_once()

        persistidas = _unidades_persistidas(repositorio_unidades)
        assert persistidas[7].descartada is True
        assert persistidas[8].descartada is True

    def test_persiste_todo_el_lote_en_una_sola_llamada(self):
        uc, repositorio_unidades, _ = _use_case()

        uc.ejecutar(
            42,
            [
                CambioUnidadAlicuota(7, descartada=True),
                CambioUnidadAlicuota(8, monto_asegurado_personalizado=1500),
                CambioUnidadAlicuota(9, descartada=False, monto_asegurado_personalizado=None),
            ],
            MagicMock(rut='1'),
        )

        repositorio_unidades.actualizar_unidades.assert_called_once()
        assert len(_unidades_persistidas(repositorio_unidades)) == 3
        repositorio_unidades.listar_por_oportunidad.assert_called_once_with(42)

    def test_cada_cambio_conserva_los_campos_no_informados(self):
        uc, repositorio_unidades, _ = _use_case(unidades=[
            _unidad(descartada=True, monto_asegurado_personalizado=900.0),
        ])

        actualizadas = uc.ejecutar(
            42,
            [CambioUnidadAlicuota(7, monto_asegurado_personalizado=1500)],
            MagicMock(rut='1'),
        )

        assert actualizadas[0].descartada is True
        assert actualizadas[0].monto_asegurado_personalizado == 1500.0

        persistidas = _unidades_persistidas(repositorio_unidades)
        assert persistidas[7].descartada is True
        assert persistidas[7].monto_asegurado_personalizado == 1500.0

    def test_monto_nulo_vuelve_al_monto_sugerido(self):
        uc, repositorio_unidades, _ = _use_case(unidades=[
            _unidad(monto_asegurado_personalizado=1500.0),
        ])

        actualizadas = uc.ejecutar(
            42,
            [CambioUnidadAlicuota(7, monto_asegurado_personalizado=None)],
            MagicMock(rut='1'),
        )

        assert actualizadas[0].monto_asegurado_personalizado is None
        assert _unidades_persistidas(repositorio_unidades)[7].monto_asegurado_personalizado is None

    def test_retorna_las_unidades_en_el_orden_de_los_cambios(self):
        uc, _, _ = _use_case()

        actualizadas = uc.ejecutar(
            42,
            [
                CambioUnidadAlicuota(9, descartada=True),
                CambioUnidadAlicuota(7, descartada=True),
            ],
            MagicMock(rut='1'),
        )

        assert [unidad.id for unidad in actualizadas] == [9, 7]

    @pytest.mark.parametrize('monto', [0, -100, float('inf'), float('nan')])
    def test_monto_invalido_es_conflicto(self, monto):
        uc, repositorio_unidades, _ = _use_case()

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar(
                42,
                [CambioUnidadAlicuota(7, monto_asegurado_personalizado=monto)],
                MagicMock(rut='1'),
            )

        repositorio_unidades.actualizar_unidades.assert_not_called()

    def test_si_un_cambio_es_invalido_no_se_persiste_nada(self):
        uc, repositorio_unidades, _ = _use_case()

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar(
                42,
                [
                    CambioUnidadAlicuota(7, descartada=True),
                    CambioUnidadAlicuota(8, monto_asegurado_personalizado=-1),
                ],
                MagicMock(rut='1'),
            )

        repositorio_unidades.actualizar_unidades.assert_not_called()

    def test_unidad_de_otra_oportunidad_no_se_encuentra(self):
        uc, repositorio_unidades, _ = _use_case()

        with pytest.raises(RecursoNoEncontradoException) as excinfo:
            uc.ejecutar(
                42,
                [
                    CambioUnidadAlicuota(7, descartada=True),
                    CambioUnidadAlicuota(99, descartada=True),
                ],
                MagicMock(rut='1'),
            )

        assert '99' in str(excinfo.value)
        repositorio_unidades.actualizar_unidades.assert_not_called()

    def test_ids_duplicados_son_conflicto(self):
        uc, repositorio_unidades, _ = _use_case()

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar(
                42,
                [
                    CambioUnidadAlicuota(7, descartada=True),
                    CambioUnidadAlicuota(7, monto_asegurado_personalizado=1500),
                ],
                MagicMock(rut='1'),
            )

        repositorio_unidades.actualizar_unidades.assert_not_called()

    def test_lote_vacio_es_conflicto(self):
        uc, repositorio_unidades, _ = _use_case()

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar(42, [], MagicMock(rut='1'))

        repositorio_unidades.actualizar_unidades.assert_not_called()

    def test_sin_permiso_es_rechazado(self):
        uc, repositorio_unidades, _ = _use_case(autorizado=False)

        with pytest.raises(UsuarioNoAutorizadoException):
            uc.ejecutar(42, [CambioUnidadAlicuota(7, descartada=True)], MagicMock(rut='1'))

        repositorio_unidades.actualizar_unidades.assert_not_called()

    def test_oportunidad_cerrada_es_conflicto(self):
        uc, _, _ = _use_case(proceso=_proceso(cerrado=True))

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar(42, [CambioUnidadAlicuota(7, descartada=True)], MagicMock(rut='1'))

    def test_oportunidad_que_no_es_de_unidades_es_conflicto(self):
        uc, _, _ = _use_case(proceso=_proceso(codigo_producto='espacios_comunes'))

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar(42, [CambioUnidadAlicuota(7, descartada=True)], MagicMock(rut='1'))

    def test_oportunidad_no_encontrada(self):
        uc, _, _ = _use_case(proceso=MagicMock(id=None))

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar(99, [CambioUnidadAlicuota(7, descartada=True)], MagicMock(rut='1'))

    def test_los_campos_no_informados_usan_la_marca_sin_cambio(self):
        cambio = CambioUnidadAlicuota(7)

        assert cambio.descartada is SIN_CAMBIO
        assert cambio.monto_asegurado_personalizado is SIN_CAMBIO


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
