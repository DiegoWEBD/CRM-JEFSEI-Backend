from unittest.mock import MagicMock

import pytest

from app.aplicacion.proceso_comercial.use_cases.importar_alicuota_oportunidad import (
    ImportarAlicuotaOportunidadUseCase,
)
from app.aplicacion.proceso_comercial.use_cases.obtener_alicuota_oportunidad import (
    ObtenerAlicuotaOportunidadUseCase,
)
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.solicitud_cotizacion.repositorio_unidades_alicuotas import RepositorioUnidadesAlicuotas
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.unidad_alicuota import UnidadAlicuota

AUSENTE = object()


def _proceso(cerrado=False, codigo_producto='unidades'):
    proceso = MagicMock()
    proceso.id = 42
    proceso.cerrado = cerrado
    proceso.producto.codigo = codigo_producto
    return proceso


def _unidades():
    return [
        UnidadAlicuota(identificador_unidad='Depto 1', prorrateo=0.025, fila_origen=2),
        UnidadAlicuota(identificador_unidad='Depto 2', prorrateo=0.015, fila_origen=3),
    ]


def _use_case_importar(proceso=AUSENTE, autorizado=True):
    repositorio_procesos = MagicMock(spec=RepositorioProcesosComerciales)
    repositorio_procesos.buscar.return_value = _proceso() if proceso is AUSENTE else proceso

    repositorio_unidades = MagicMock(spec=RepositorioUnidadesAlicuotas)

    authorization = MagicMock()
    authorization.usuario_puede_solicitar_cotizacion.return_value = autorizado

    uc = ImportarAlicuotaOportunidadUseCase(
        repositorio_procesos,
        repositorio_unidades,
        authorization,
    )
    return uc, repositorio_unidades


def _use_case_obtener(unidades=None, nombre_excel='alicuota.xlsx', autorizado=True):
    repositorio_procesos = MagicMock(spec=RepositorioProcesosComerciales)
    repositorio_procesos.buscar.return_value = _proceso()

    repositorio_unidades = MagicMock(spec=RepositorioUnidadesAlicuotas)
    repositorio_unidades.listar_por_oportunidad.return_value = (
        _unidades() if unidades is None else unidades
    )
    repositorio_unidades.obtener_nombre_excel.return_value = nombre_excel

    authorization = MagicMock()
    authorization.usuario_puede_ver_solicitudes_cotizacion.return_value = autorizado

    uc = ObtenerAlicuotaOportunidadUseCase(
        repositorio_procesos,
        repositorio_unidades,
        authorization,
    )
    return uc, repositorio_unidades


@pytest.mark.unit
class TestImportarAlicuotaOportunidad:

    def test_guarda_las_unidades_en_la_oportunidad(self):
        uc, repositorio_unidades = _use_case_importar()
        unidades = _unidades()

        uc.ejecutar(42, 'alicuota.xlsx', unidades, MagicMock(rut='1'))

        repositorio_unidades.guardar_o_reemplazar.assert_called_once_with(42, 'alicuota.xlsx', unidades)

    def test_oportunidad_no_encontrada(self):
        uc, repositorio_unidades = _use_case_importar(proceso=None)

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar(99, 'alicuota.xlsx', _unidades(), MagicMock(rut='1'))

        repositorio_unidades.guardar_o_reemplazar.assert_not_called()

    def test_sin_permiso_es_rechazado(self):
        uc, repositorio_unidades = _use_case_importar(autorizado=False)

        with pytest.raises(UsuarioNoAutorizadoException):
            uc.ejecutar(42, 'alicuota.xlsx', _unidades(), MagicMock(rut='1'))

        repositorio_unidades.guardar_o_reemplazar.assert_not_called()

    def test_oportunidad_cerrada_es_conflicto(self):
        uc, _ = _use_case_importar(proceso=_proceso(cerrado=True))

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar(42, 'alicuota.xlsx', _unidades(), MagicMock(rut='1'))

    def test_oportunidad_que_no_es_de_unidades_es_conflicto(self):
        uc, _ = _use_case_importar(proceso=_proceso(codigo_producto='espacios_comunes'))

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar(42, 'alicuota.xlsx', _unidades(), MagicMock(rut='1'))

    def test_sin_nombre_excel_es_conflicto(self):
        uc, _ = _use_case_importar()

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar(42, '  ', _unidades(), MagicMock(rut='1'))

    def test_unidades_invalidas_son_conflicto(self):
        uc, repositorio_unidades = _use_case_importar()
        unidades = [UnidadAlicuota(identificador_unidad='  ', prorrateo=0.025, fila_origen=2)]

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar(42, 'alicuota.xlsx', unidades, MagicMock(rut='1'))

        repositorio_unidades.guardar_o_reemplazar.assert_not_called()

    def test_reemplaza_la_alicuota_previa(self):
        # guardar_o_reemplazar es transaccional: la alícuota anterior se descarta
        uc, repositorio_unidades = _use_case_importar()

        uc.ejecutar(42, 'nueva.xlsx', _unidades(), MagicMock(rut='1'))
        uc.ejecutar(42, 'otra.xlsx', _unidades(), MagicMock(rut='1'))

        assert repositorio_unidades.guardar_o_reemplazar.call_count == 2


@pytest.mark.unit
class TestObtenerAlicuotaOportunidad:

    def test_devuelve_nombre_excel_y_unidades(self):
        uc, repositorio_unidades = _use_case_obtener()

        nombre_excel, unidades = uc.ejecutar(42, MagicMock(rut='1'))

        assert nombre_excel == 'alicuota.xlsx'
        assert [u.identificador_unidad for u in unidades] == ['Depto 1', 'Depto 2']
        repositorio_unidades.listar_por_oportunidad.assert_called_once_with(42)

    def test_sin_alicuota_devuelve_nombre_nulo(self):
        uc, _ = _use_case_obtener(unidades=[], nombre_excel=None)

        nombre_excel, unidades = uc.ejecutar(42, MagicMock(rut='1'))

        assert nombre_excel is None
        assert unidades == []

    def test_oportunidad_no_encontrada(self):
        uc, repositorio_unidades = _use_case_obtener()
        uc.repositorio_procesos_comerciales.buscar.return_value = None

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar(99, MagicMock(rut='1'))

        repositorio_unidades.listar_por_oportunidad.assert_not_called()

    def test_sin_permiso_es_rechazado(self):
        uc, repositorio_unidades = _use_case_obtener(autorizado=False)

        with pytest.raises(UsuarioNoAutorizadoException):
            uc.ejecutar(42, MagicMock(rut='1'))

        repositorio_unidades.listar_por_oportunidad.assert_not_called()
