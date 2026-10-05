import pytest
from unittest.mock import MagicMock, patch

from app.aplicacion.notificacion.use_cases.generar_alertas_sla import GenerarAlertasSlaUseCase
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from tests.factories.notificacion_factory import (
    AHORA_REF,
    crear_proceso_alertable_sla_mock,
)


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioNotificaciones)


def _alertables(*procesos):
    return list(procesos)


def _use_case(repositorio_mock, *procesos, registrar_retorno: bool = True):
    repositorio_mock.obtener_procesos_alertables.return_value = _alertables(*procesos)
    repositorio_mock.registrar.return_value = registrar_retorno
    return GenerarAlertasSlaUseCase(repositorio_mock)


@pytest.mark.unit
class TestGenerarAlertasSlaUmbrales:

    def test_dentro_del_umbral_no_genera_alerta(self, repositorio_mock):
        # 6 de 10 días -> 0.60 (< 0.70) -> verde, sin alerta
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=6, dias_limite=10, ahora=AHORA_REF
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert creadas == []
        repositorio_mock.registrar.assert_not_called()

    def test_cerca_del_limite_genera_por_vencer_aviso(self, repositorio_mock):
        # 7 de 10 días -> 0.70 -> amarillo
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=7, dias_limite=10, ahora=AHORA_REF
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert creadas[0].codigo_tipo == "SLA_POR_VENCER"
        assert creadas[0].nivel == "AVISO"

    def test_exactamente_en_el_limite_sigue_siendo_por_vencer(self, repositorio_mock):
        # 10 de 10 días -> 1.00 (<= 1.0) -> aún amarillo
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=10, dias_limite=10, ahora=AHORA_REF
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert creadas[0].codigo_tipo == "SLA_POR_VENCER"
        assert creadas[0].nivel == "AVISO"

    def test_sobre_el_limite_genera_vencido_critico(self, repositorio_mock):
        # 11 de 10 días -> 1.10 (> 1.0) -> rojo
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=11, dias_limite=10, ahora=AHORA_REF
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert creadas[0].codigo_tipo == "SLA_VENCIDO"
        assert creadas[0].nivel == "CRITICO"

    def test_dias_limite_del_estado_no_de_la_etapa(self, repositorio_mock):
        # El estado límite 10 (0.70 -> alerta) pero la etapa dice 1 (11.0 -> se descarta
        # si se usara por error el límite de la etapa, entraría en vencido).
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=7,
            dias_limite=10,
            dias_limite_etapa=1,
            ahora=AHORA_REF,
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert creadas[0].codigo_tipo == "SLA_POR_VENCER"

    def test_estado_sin_dias_limite_no_genera(self, repositorio_mock):
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=11, dias_limite=None, ahora=AHORA_REF
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert creadas == []
        repositorio_mock.registrar.assert_not_called()


@pytest.mark.unit
class TestGenerarAlertasSlaDestinatarios:

    def test_rol_comercial_dirige_a_rut_ej_comercial(self, repositorio_mock):
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=11,
            dias_limite=10,
            rol_responsable_siguiente="EJECUTIVO_COMERCIAL",
            rut_ej_comercial="11111111-1",
            rut_ej_evaluacion="22222222-2",
            ahora=AHORA_REF,
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert creadas[0].rut_usuario == "11111111-1"

    def test_rol_evaluacion_dirige_a_rut_ej_evaluacion(self, repositorio_mock):
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=11,
            dias_limite=10,
            rol_responsable_siguiente="EJECUTIVO_EVALUACION_PROYECTOS",
            rut_ej_comercial="11111111-1",
            rut_ej_evaluacion="22222222-2",
            ahora=AHORA_REF,
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert creadas[0].rut_usuario == "22222222-2"

    def test_rol_sin_mapeo_hace_fan_out(self, repositorio_mock):
        # Rol fuera del mapeo (GERENTE_COMERCIAL) -> fan-out a todos los
        # usuarios activos con ese rol.
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=11,
            dias_limite=10,
            rol_responsable_siguiente="GERENTE_COMERCIAL",
            rut_ej_comercial="11111111-1",
            rut_ej_evaluacion="22222222-2",
            ahora=AHORA_REF,
        )
        repositorio_mock.obtener_ruts_por_roles.return_value = {
            'GERENTE_COMERCIAL': ['33333333-3'],
        }
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert creadas[0].rut_usuario == "33333333-3"
        repositorio_mock.obtener_ruts_por_roles.assert_called_once_with(
            ['GERENTE_COMERCIAL']
        )

    def test_fan_out_multiples_usuarios(self, repositorio_mock):
        # Varios usuarios con el mismo rol -> una alerta por cada uno.
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=11,
            dias_limite=10,
            rol_responsable_siguiente="GERENTE_COMERCIAL",
            ahora=AHORA_REF,
        )
        repositorio_mock.obtener_ruts_por_roles.return_value = {
            'GERENTE_COMERCIAL': ['33333333-3', '44444444-4'],
        }
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 2
        ruts = {n.rut_usuario for n in creadas}
        assert ruts == {'33333333-3', '44444444-4'}

    def test_fan_out_sin_usuarios_no_genera(self, repositorio_mock):
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=11,
            dias_limite=10,
            rol_responsable_siguiente="GERENTE_COMERCIAL",
            ahora=AHORA_REF,
        )
        repositorio_mock.obtener_ruts_por_roles.return_value = {
            'GERENTE_COMERCIAL': [],
        }
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert creadas == []
        repositorio_mock.registrar.assert_not_called()

    def test_estado_sin_rol_responsable_siguiente_no_genera(self, repositorio_mock):
        # Sin transición principal (rol_responsable_siguiente = None) -> sin alerta.
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=11,
            dias_limite=10,
            rol_responsable_siguiente=None,
            ahora=AHORA_REF,
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert creadas == []
        repositorio_mock.registrar.assert_not_called()

    def test_campo_destino_sin_asignado_no_genera(self, repositorio_mock):
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=11,
            dias_limite=10,
            rol_responsable_siguiente="EJECUTIVO_COMERCIAL",
            rut_ej_comercial=None,
            ahora=AHORA_REF,
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert creadas == []
        repositorio_mock.registrar.assert_not_called()


@pytest.mark.unit
class TestGenerarAlertasSlaCasosLimite:

    def test_proceso_cerrado_no_genera_alertas(self, repositorio_mock):
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=11, dias_limite=10, cerrado=True, ahora=AHORA_REF
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert creadas == []
        repositorio_mock.registrar.assert_not_called()

    def test_no_duplica_alerta_existente(self, repositorio_mock):
        # registrar devuelve False cuando la dedupe_key ya existia (ON CONFLICT DO NOTHING)
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=11, dias_limite=10, ahora=AHORA_REF
        )
        uc = _use_case(repositorio_mock, proceso, registrar_retorno=False)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert creadas == []
        repositorio_mock.registrar.assert_called_once()

    def test_dedupe_key_incluye_tipo_proceso_estado_y_rut(self, repositorio_mock):
        proceso = crear_proceso_alertable_sla_mock(
            id_proceso_comercial=42,
            codigo_estado="CONTACTO_INICIAL",
            dias_transcurridos=11,
            dias_limite=10,
            rut_ej_comercial="11111111-1",
            ahora=AHORA_REF,
        )
        uc = _use_case(repositorio_mock, proceso)

        uc.ejecutar(ahora=AHORA_REF)

        notificacion = repositorio_mock.registrar.call_args.args[0]
        assert notificacion.dedupe_key == "SLA_VENCIDO:42:CONTACTO_INICIAL:11111111-1"

    def test_cambio_de_estado_genera_clave_nueva(self, repositorio_mock):
        repositorio_mock.obtener_procesos_alertables.return_value = [
            crear_proceso_alertable_sla_mock(
                codigo_estado="CONTACTO_INICIAL",
                dias_transcurridos=11,
                dias_limite=10,
                rut_ej_comercial="11111111-1",
                ahora=AHORA_REF,
            )
        ]
        uc = GenerarAlertasSlaUseCase(repositorio_mock)

        uc.ejecutar(ahora=AHORA_REF)
        clave_primera = repositorio_mock.registrar.call_args.args[0].dedupe_key

        repositorio_mock.obtener_procesos_alertables.return_value = [
            crear_proceso_alertable_sla_mock(
                codigo_estado="PROPUESTA_ENVIADA",
                dias_transcurridos=11,
                dias_limite=10,
                rut_ej_comercial="11111111-1",
                ahora=AHORA_REF,
            )
        ]
        repositorio_mock.registrar.reset_mock()
        repositorio_mock.registrar.return_value = True
        uc.ejecutar(ahora=AHORA_REF)
        clave_segunda = repositorio_mock.registrar.call_args.args[0].dedupe_key

        assert clave_primera != clave_segunda

    def test_alertas_generadas_estan_sin_leer(self, repositorio_mock):
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=11, dias_limite=10, ahora=AHORA_REF
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert creadas[0].leida is False
        assert creadas[0].fecha_leida is None
        assert creadas[0].entidad_tipo == "PROCESO_COMERCIAL"
        assert creadas[0].entidad_id == 1
        assert creadas[0].id_prospecto == 1

    def test_sin_procesos_alertables_retorna_vacio(self, repositorio_mock):
        repositorio_mock.obtener_procesos_alertables.return_value = []
        uc = GenerarAlertasSlaUseCase(repositorio_mock)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert creadas == []
        repositorio_mock.registrar.assert_not_called()

    def test_mensaje_usa_accion_requerida_cuando_existe(self, repositorio_mock):
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=7,
            dias_limite=10,
            accion_requerida="cargar cotizaciones",
            ahora=AHORA_REF,
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert "— falta cargar cotizaciones" in creadas[0].mensaje

    def test_mensaje_usa_nombre_siguiente_estado_como_fallback(self, repositorio_mock):
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=7,
            dias_limite=10,
            accion_requerida=None,
            nombre_siguiente_estado="Cotización disponible",
            ahora=AHORA_REF,
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert "— pendiente en Cotización disponible" in creadas[0].mensaje

    def test_accion_requerida_tiene_prioridad_sobre_nombre(self, repositorio_mock):
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=7,
            dias_limite=10,
            accion_requerida="solicitar cotización",
            nombre_siguiente_estado="Cotización solicitada",
            ahora=AHORA_REF,
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert "— falta solicitar cotización" in creadas[0].mensaje
        assert "pendiente" not in creadas[0].mensaje

    def test_alertas_sla_no_son_leibles(self, repositorio_mock):
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=11,
            dias_limite=10,
            ahora=AHORA_REF,
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert creadas[0].leible is False


@pytest.mark.unit
class TestGenerarAlertasSlaPublicacion:
    """El aviso por WebSocket vive en el use case: el scheduler solo loguea."""

    def test_publica_a_los_destinatarios_de_las_creadas(self, repositorio_mock):
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=11,
            dias_limite=10,
            rol_responsable_siguiente="EJECUTIVO_COMERCIAL",
            rut_ej_comercial="11111111-1",
            ahora=AHORA_REF,
        )
        uc = _use_case(repositorio_mock, proceso)

        with patch.object(hub, 'publicar_desde_hilo') as publicar:
            uc.ejecutar(ahora=AHORA_REF)

        publicar.assert_called_once()
        ruts, payload = publicar.call_args.args
        assert list(ruts) == ["11111111-1"]
        assert payload == {
            'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS,
            'motivo': 'alertas_generadas',
        }

    def test_no_publica_si_no_creo_nada(self, repositorio_mock):
        # Sin candidatos (o todas con dedupe ya existente) no hay nada que avisar.
        repositorio_mock.obtener_procesos_alertables.return_value = []
        uc = GenerarAlertasSlaUseCase(repositorio_mock)

        with patch.object(hub, 'publicar_desde_hilo') as publicar:
            uc.ejecutar(ahora=AHORA_REF)

        publicar.assert_not_called()

    def test_no_publica_si_todo_ya_estaba_registrado(self, repositorio_mock):
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=11, dias_limite=10, ahora=AHORA_REF
        )
        uc = _use_case(repositorio_mock, proceso, registrar_retorno=False)

        with patch.object(hub, 'publicar_desde_hilo') as publicar:
            creadas = uc.ejecutar(ahora=AHORA_REF)

        assert creadas == []
        publicar.assert_not_called()
