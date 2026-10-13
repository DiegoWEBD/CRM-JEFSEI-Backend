from unittest.mock import MagicMock

import pytest

from app.aplicacion.estado.use_cases.actualizar_estado_configuracion import ActualizarEstadoConfiguracionUseCase
from app.aplicacion.estado.use_cases.actualizar_transicion import ActualizarTransicionUseCase
from app.aplicacion.estado.use_cases.crear_transicion import CrearTransicionUseCase
from app.dominio.estado_informativo_proceso_comercial.repositorio_estados_proceso_comercial import RepositorioEstadosProcesoComercial
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from tests.factories.transicion_factory import crear_transicion_mock


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioEstadosProcesoComercial)


def _estado_mock(**kwargs):
    from app.dominio.estado_informativo_proceso_comercial.estado_informativo_proceso_comercial import EstadoInformativoProcesoComercial
    from app.dominio.etapa_proceso_comercial.etapa_proceso_comercial import EtapaProcesoComercial

    etapa = EtapaProcesoComercial(
        codigo="ETAPA_1",
        nombre="Prospección",
        sigiuente_etapa=None,
        dias_limite=None,
    )
    defaults = {
        'codigo': 'ESTADO_ORIGEN',
        'etapa': etapa,
        'nombre': 'Estado Origen',
    }
    defaults.update(kwargs)
    return EstadoInformativoProcesoComercial(**defaults)


@pytest.mark.unit
class TestCrearTransicionUseCase:

    @pytest.fixture
    def use_case(self, repositorio_mock):
        return CrearTransicionUseCase(repositorio_estados=repositorio_mock)

    def test_crear_transicion_secundaria_exitosa(self, use_case, repositorio_mock):
        repositorio_mock.obtener_por_codigo.side_effect = [
            _estado_mock(codigo='ESTADO_ORIGEN'),
            _estado_mock(codigo='ESTADO_DESTINO', nombre='Estado Destino'),
        ]
        repositorio_mock.existe_transicion.return_value = False
        repositorio_mock.crear_transicion.return_value = True

        resultado = use_case.ejecutar(
            codigo_estado_origen='ESTADO_ORIGEN',
            codigo_estado_destino='ESTADO_DESTINO',
            es_manual=True,
            es_principal=False,
            accion_requerida='cargar cotizaciones',
        )

        assert resultado is True
        transicion = repositorio_mock.crear_transicion.call_args.args[0]
        assert transicion.es_principal is False
        assert transicion.dias_limite is None

    def test_crear_transicion_principal_lanza_excepcion(self, use_case, repositorio_mock):
        """Las transiciones principales definen el SLA: no se pueden crear
        desde la API, solo se siembran por migración."""
        repositorio_mock.obtener_por_codigo.side_effect = [
            _estado_mock(codigo='ESTADO_ORIGEN'),
            _estado_mock(codigo='ESTADO_DESTINO', nombre='Estado Destino'),
        ]

        with pytest.raises(ConflictoEnAccionException):
            use_case.ejecutar(
                codigo_estado_origen='ESTADO_ORIGEN',
                codigo_estado_destino='ESTADO_DESTINO',
                es_manual=True,
                es_principal=True,
            )

        repositorio_mock.crear_transicion.assert_not_called()

    def test_crear_transicion_estado_inexistente_lanza_excepcion(
        self, use_case, repositorio_mock
    ):
        repositorio_mock.obtener_por_codigo.return_value = None

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(
                codigo_estado_origen='NO_EXISTE',
                codigo_estado_destino='ESTADO_DESTINO',
            )

        repositorio_mock.crear_transicion.assert_not_called()


@pytest.mark.unit
class TestActualizarTransicionUseCase:

    @pytest.fixture
    def use_case(self, repositorio_mock):
        return ActualizarTransicionUseCase(repositorio_estados=repositorio_mock)

    def test_actualizar_secundaria_actualiza_es_manual_y_accion(
        self, use_case, repositorio_mock
    ):
        repositorio_mock.obtener_transicion.return_value = crear_transicion_mock(
            es_manual=False,
            accion_requerida=None,
            dias_limite=None,
        )
        repositorio_mock.actualizar_transicion.return_value = True

        resultado = use_case.ejecutar(
            codigo_estado_origen='ESTADO_ORIGEN',
            codigo_estado_destino='ESTADO_DESTINO',
            es_manual=True,
            accion_requerida='cargar cotizaciones',
        )

        assert resultado is True
        transicion = repositorio_mock.actualizar_transicion.call_args.args[0]
        assert transicion.es_manual is True
        assert transicion.accion_requerida == 'cargar cotizaciones'
        # Una transición secundaria nunca tiene días límite de SLA.
        assert transicion.dias_limite is None

    def test_actualizar_principal_solo_cambia_dias_limite(
        self, use_case, repositorio_mock
    ):
        """La principal es editable únicamente en su días límite (SLA):
        es_manual y accion_requerida quedan intactas."""
        repositorio_mock.obtener_transicion.return_value = crear_transicion_mock(
            es_principal=True,
            es_manual=True,
            accion_requerida='gestionar aceptación de propuesta',
            dias_limite=10,
        )
        repositorio_mock.actualizar_transicion.return_value = True

        resultado = use_case.ejecutar(
            codigo_estado_origen='ESTADO_ORIGEN',
            codigo_estado_destino='ESTADO_DESTINO',
            es_manual=True,
            accion_requerida='gestionar aceptación de propuesta',
            dias_limite=15,
        )

        assert resultado is True
        transicion = repositorio_mock.actualizar_transicion.call_args.args[0]
        assert transicion.dias_limite == 15
        assert transicion.es_manual is True
        assert transicion.accion_requerida == 'gestionar aceptación de propuesta'

    def test_actualizar_principal_puede_limpiar_dias_limite(
        self, use_case, repositorio_mock
    ):
        repositorio_mock.obtener_transicion.return_value = crear_transicion_mock(
            es_principal=True,
            dias_limite=10,
        )
        repositorio_mock.actualizar_transicion.return_value = True

        use_case.ejecutar(
            codigo_estado_origen='ESTADO_ORIGEN',
            codigo_estado_destino='ESTADO_DESTINO',
            es_manual=True,
            accion_requerida=None,
            dias_limite=None,
        )

        transicion = repositorio_mock.actualizar_transicion.call_args.args[0]
        assert transicion.dias_limite is None

    def test_actualizar_principal_con_dias_limite_negativo_lanza_conflicto(
        self, use_case, repositorio_mock
    ):
        repositorio_mock.obtener_transicion.return_value = crear_transicion_mock(
            es_principal=True,
            dias_limite=10,
        )

        with pytest.raises(ConflictoEnAccionException):
            use_case.ejecutar(
                codigo_estado_origen='ESTADO_ORIGEN',
                codigo_estado_destino='ESTADO_DESTINO',
                es_manual=True,
                accion_requerida=None,
                dias_limite=-1,
            )

        repositorio_mock.actualizar_transicion.assert_not_called()

    def test_transicion_inexistente_lanza_excepcion(self, use_case, repositorio_mock):
        repositorio_mock.obtener_transicion.return_value = None

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(
                codigo_estado_origen='ESTADO_ORIGEN',
                codigo_estado_destino='NO_EXISTE',
                es_manual=True,
                accion_requerida=None,
            )


@pytest.mark.unit
class TestActualizarEstadoConfiguracionUseCase:

    @pytest.fixture
    def use_case(self, repositorio_mock):
        return ActualizarEstadoConfiguracionUseCase(repositorio_estados=repositorio_mock)

    def test_configuracion_actualiza_solo_probabilidad(self, use_case, repositorio_mock):
        """Los días límite ya no viven en el estado (están en su transición
        principal): la configuración del estado solo toca la probabilidad."""
        repositorio_mock.obtener_por_codigo.return_value = _estado_mock()
        repositorio_mock.actualizar_configuracion.return_value = True

        resultado = use_case.ejecutar(
            codigo='ESTADO_ORIGEN',
            probabilidad_cierre=0.5,
        )

        assert resultado is True
        repositorio_mock.actualizar_configuracion.assert_called_once_with(
            codigo='ESTADO_ORIGEN',
            probabilidad_cierre=0.5,
        )

    def test_probabilidad_fuera_de_rango_lanza_conflicto(self, use_case, repositorio_mock):
        repositorio_mock.obtener_por_codigo.return_value = _estado_mock()

        with pytest.raises(ConflictoEnAccionException):
            use_case.ejecutar(codigo='ESTADO_ORIGEN', probabilidad_cierre=1.5)

        with pytest.raises(ConflictoEnAccionException):
            use_case.ejecutar(codigo='ESTADO_ORIGEN', probabilidad_cierre=-0.1)

        repositorio_mock.actualizar_configuracion.assert_not_called()

    def test_estado_inexistente_lanza_excepcion(self, use_case, repositorio_mock):
        repositorio_mock.obtener_por_codigo.return_value = None

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(codigo='NO_EXISTE', probabilidad_cierre=0.5)

        repositorio_mock.actualizar_configuracion.assert_not_called()
