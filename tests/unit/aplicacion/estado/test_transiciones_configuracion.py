from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.estado.use_cases.actualizar_estado_configuracion import ActualizarEstadoConfiguracionUseCase
from app.aplicacion.estado.use_cases.actualizar_transicion import ActualizarTransicionUseCase
from app.aplicacion.estado.use_cases.crear_transicion import CrearTransicionUseCase
from app.aplicacion.notificacion.use_cases.generar_alertas_sla import GenerarAlertasSlaUseCase
from app.dominio.estado_informativo_proceso_comercial.repositorio_estados_proceso_comercial import RepositorioEstadosProcesoComercial
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from tests.factories.notificacion_factory import crear_notificacion_mock
from tests.factories.transicion_factory import crear_transicion_mock

MODULO_ACTUALIZAR_TRANSICION = 'app.aplicacion.estado.use_cases.actualizar_transicion.hub'


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioEstadosProcesoComercial)


@pytest.fixture
def repositorio_notificaciones_mock():
    return MagicMock(spec=RepositorioNotificaciones)


@pytest.fixture
def generar_alertas_sla_mock():
    return MagicMock(spec=GenerarAlertasSlaUseCase)


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
    def use_case(
        self,
        repositorio_mock,
        repositorio_notificaciones_mock,
        generar_alertas_sla_mock,
    ):
        return ActualizarTransicionUseCase(
            repositorio_estados=repositorio_mock,
            repositorio_notificaciones=repositorio_notificaciones_mock,
            generar_alertas_sla=generar_alertas_sla_mock,
        )

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

    def test_actualizar_principal_con_cambio_elimina_sla_no_leidas_y_reevalua(
        self,
        use_case,
        repositorio_mock,
        repositorio_notificaciones_mock,
        generar_alertas_sla_mock,
    ):
        """Un cambio de días límite borra las alertas SLA no leídas del estado
        y las re-evalúa de inmediato con el nuevo límite."""
        repositorio_mock.obtener_transicion.return_value = crear_transicion_mock(
            es_principal=True,
            dias_limite=10,
        )
        repositorio_mock.actualizar_transicion.return_value = True

        alerta_vencida = crear_notificacion_mock(
            id=1, rut_usuario='11111111-1', codigo_tipo='SLA_VENCIDO'
        )
        alerta_por_vencer = crear_notificacion_mock(
            id=2, rut_usuario='22222222-2', codigo_tipo='SLA_POR_VENCER'
        )
        repositorio_notificaciones_mock.obtener_todas.return_value = [
            alerta_vencida,
            alerta_por_vencer,
        ]

        with patch(MODULO_ACTUALIZAR_TRANSICION) as hub_mock:
            resultado = use_case.ejecutar(
                codigo_estado_origen='ESTADO_ORIGEN',
                codigo_estado_destino='ESTADO_DESTINO',
                es_manual=True,
                accion_requerida=None,
                dias_limite=5,
            )

        assert resultado is True
        repositorio_notificaciones_mock.obtener_todas.assert_called_once_with(
            codigo_estado='ESTADO_ORIGEN', leidas=False
        )
        assert repositorio_notificaciones_mock.eliminar.call_count == 2
        eliminadas = [
            llamada.args[0]
            for llamada in repositorio_notificaciones_mock.eliminar.call_args_list
        ]
        assert alerta_vencida in eliminadas
        assert alerta_por_vencer in eliminadas

        generar_alertas_sla_mock.ejecutar.assert_called_once_with()

        hub_mock.publicar_desde_hilo.assert_called_once()
        ruts, payload = hub_mock.publicar_desde_hilo.call_args.args
        assert set(ruts) == {'11111111-1', '22222222-2'}
        assert payload['motivo'] == 'sla_reevaluado'

    def test_reevaluar_solo_elimina_alertas_de_tipo_sla(
        self,
        use_case,
        repositorio_mock,
        repositorio_notificaciones_mock,
        generar_alertas_sla_mock,
    ):
        repositorio_mock.obtener_transicion.return_value = crear_transicion_mock(
            es_principal=True,
            dias_limite=10,
        )
        repositorio_mock.actualizar_transicion.return_value = True

        alerta_sla = crear_notificacion_mock(
            id=1, rut_usuario='11111111-1', codigo_tipo='SLA_VENCIDO'
        )
        notificacion_asignacion = crear_notificacion_mock(
            id=2,
            rut_usuario='11111111-1',
            codigo_tipo='ASIGNACION_EJECUTIVO',
            nivel='INFO',
            leible=True,
        )
        repositorio_notificaciones_mock.obtener_todas.return_value = [
            alerta_sla,
            notificacion_asignacion,
        ]

        with patch(MODULO_ACTUALIZAR_TRANSICION) as hub_mock:
            use_case.ejecutar(
                codigo_estado_origen='ESTADO_ORIGEN',
                codigo_estado_destino='ESTADO_DESTINO',
                es_manual=True,
                accion_requerida=None,
                dias_limite=3,
            )

        repositorio_notificaciones_mock.eliminar.assert_called_once_with(alerta_sla)
        generar_alertas_sla_mock.ejecutar.assert_called_once_with()
        ruts, _ = hub_mock.publicar_desde_hilo.call_args.args
        assert set(ruts) == {'11111111-1'}

    def test_actualizar_principal_sin_cambio_no_toca_alertas(
        self,
        use_case,
        repositorio_mock,
        repositorio_notificaciones_mock,
        generar_alertas_sla_mock,
    ):
        """Guardar el mismo días límite no debe borrar alertas ni re-notificar."""
        repositorio_mock.obtener_transicion.return_value = crear_transicion_mock(
            es_principal=True,
            dias_limite=10,
        )
        repositorio_mock.actualizar_transicion.return_value = True

        resultado = use_case.ejecutar(
            codigo_estado_origen='ESTADO_ORIGEN',
            codigo_estado_destino='ESTADO_DESTINO',
            es_manual=True,
            accion_requerida=None,
            dias_limite=10,
        )

        assert resultado is True
        repositorio_notificaciones_mock.obtener_todas.assert_not_called()
        repositorio_notificaciones_mock.eliminar.assert_not_called()
        generar_alertas_sla_mock.ejecutar.assert_not_called()

    def test_actualizar_secundaria_no_toca_alertas(
        self,
        use_case,
        repositorio_mock,
        repositorio_notificaciones_mock,
        generar_alertas_sla_mock,
    ):
        """La transición secundaria no define SLA: su guardado no re-evalúa."""
        repositorio_mock.obtener_transicion.return_value = crear_transicion_mock(
            es_principal=False,
            dias_limite=None,
        )
        repositorio_mock.actualizar_transicion.return_value = True

        use_case.ejecutar(
            codigo_estado_origen='ESTADO_ORIGEN',
            codigo_estado_destino='ESTADO_DESTINO',
            es_manual=True,
            accion_requerida='cargar cotizaciones',
        )

        repositorio_notificaciones_mock.obtener_todas.assert_not_called()
        generar_alertas_sla_mock.ejecutar.assert_not_called()

    def test_actualizacion_fallida_no_reevalua(
        self,
        use_case,
        repositorio_mock,
        repositorio_notificaciones_mock,
        generar_alertas_sla_mock,
    ):
        repositorio_mock.obtener_transicion.return_value = crear_transicion_mock(
            es_principal=True,
            dias_limite=10,
        )
        repositorio_mock.actualizar_transicion.return_value = False

        resultado = use_case.ejecutar(
            codigo_estado_origen='ESTADO_ORIGEN',
            codigo_estado_destino='ESTADO_DESTINO',
            es_manual=True,
            accion_requerida=None,
            dias_limite=5,
        )

        assert resultado is False
        repositorio_notificaciones_mock.obtener_todas.assert_not_called()
        generar_alertas_sla_mock.ejecutar.assert_not_called()

    def test_reevaluar_sin_destinatarios_no_publica_en_hub(
        self,
        use_case,
        repositorio_mock,
        repositorio_notificaciones_mock,
        generar_alertas_sla_mock,
    ):
        """El borrado y la re-evaluación ocurren igual; solo se omite el aviso
        al hub (no hay a quién notificar la eliminación)."""
        repositorio_mock.obtener_transicion.return_value = crear_transicion_mock(
            es_principal=True,
            dias_limite=10,
        )
        repositorio_mock.actualizar_transicion.return_value = True

        repositorio_notificaciones_mock.obtener_todas.return_value = [
            crear_notificacion_mock(id=1, rut_usuario=None, codigo_tipo='SLA_VENCIDO')
        ]

        with patch(MODULO_ACTUALIZAR_TRANSICION) as hub_mock:
            use_case.ejecutar(
                codigo_estado_origen='ESTADO_ORIGEN',
                codigo_estado_destino='ESTADO_DESTINO',
                es_manual=True,
                accion_requerida=None,
                dias_limite=2,
            )

        repositorio_notificaciones_mock.eliminar.assert_called_once()
        generar_alertas_sla_mock.ejecutar.assert_called_once_with()
        hub_mock.publicar_desde_hilo.assert_not_called()


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
