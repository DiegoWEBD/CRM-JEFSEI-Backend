import pytest
from unittest.mock import MagicMock, patch

from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
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


def _servicio_alertas(marcados=None):
    servicio = MagicMock(spec=ServicioAlertasProceso)
    servicio.marcar_leidas.return_value = marcados or []
    servicio.marcar_leidas_sla_anteriores.return_value = marcados or []
    return servicio


def _use_case(repositorio_mock, *procesos, registrar_retorno: bool = True, servicio_alertas=None):
    repositorio_mock.obtener_procesos_alertables.return_value = _alertables(*procesos)
    repositorio_mock.registrar.return_value = registrar_retorno
    return GenerarAlertasSlaUseCase(
        repositorio_mock, servicio_alertas or _servicio_alertas()
    )


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

    def test_transicion_principal_sin_dias_limite_no_genera(self, repositorio_mock):
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=11, dias_limite=None, ahora=AHORA_REF
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert creadas == []
        repositorio_mock.registrar.assert_not_called()

    def test_consumo_con_fraccion_de_dia_no_alerta_bajo_el_umbral(self, repositorio_mock):
        # 0.5 de 1 día (12 h) -> 0.50 (< 0.70) -> sin alerta, aunque la
        # fracción de día ya sea medible.
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=0.5, dias_limite=1, ahora=AHORA_REF
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert creadas == []
        repositorio_mock.registrar.assert_not_called()

    def test_consumo_con_fraccion_de_dia_genera_por_vencer(self, repositorio_mock):
        # 0.75 de 1 día (18 h) -> 0.75 (>= 0.70) -> amarillo sin pasar un día
        # entero: el umbral se evalúa con precisión de horas.
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=0.75, dias_limite=1, ahora=AHORA_REF
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert creadas[0].codigo_tipo == "SLA_POR_VENCER"
        assert creadas[0].nivel == "AVISO"

    def test_consumo_con_fraccion_de_dia_genera_vencido(self, repositorio_mock):
        # 1.25 de 1 día (30 h) -> 1.25 (> 1.0) -> vencido con 6 h de atraso.
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=1.25, dias_limite=1, ahora=AHORA_REF
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert creadas[0].codigo_tipo == "SLA_VENCIDO"
        assert creadas[0].nivel == "CRITICO"


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

    def test_dedupe_key_incluye_tipo_tramo_proceso_estado_y_rut(self, repositorio_mock):
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
        assert notificacion.dedupe_key == "SLA_VENCIDO@100:42:CONTACTO_INICIAL:11111111-1"

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
        uc = GenerarAlertasSlaUseCase(repositorio_mock, _servicio_alertas())

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
        uc = GenerarAlertasSlaUseCase(repositorio_mock, _servicio_alertas())

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

    def test_mensaje_muestra_dias_y_horas_transcurridos(self, repositorio_mock):
        # 0.75 de 1 día (18 h transcurridas, 6 h restantes).
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=0.75,
            dias_limite=1,
            accion_requerida="cargar cotizaciones",
            ahora=AHORA_REF,
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert "lleva 0 días 18 h de 1 día" in creadas[0].mensaje
        assert "restan 0 días 6 h" in creadas[0].mensaje

    def test_mensaje_vencido_muestra_atraso_en_dias_y_horas(self, repositorio_mock):
        # 1.25 de 1 día -> 6 h de atraso.
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=1.25,
            dias_limite=1,
            accion_requerida="cargar cotizaciones",
            ahora=AHORA_REF,
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert "lleva 1 día 6 h de 1 día" in creadas[0].mensaje
        assert "(+0 días 6 h de atraso)" in creadas[0].mensaje

    def test_mensaje_con_horas_en_cero_omite_las_horas(self, repositorio_mock):
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=7,
            dias_limite=10,
            accion_requerida="cargar cotizaciones",
            ahora=AHORA_REF,
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert "lleva 7 días de 10 días" in creadas[0].mensaje
        assert "restan 3 días" in creadas[0].mensaje

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
        uc = GenerarAlertasSlaUseCase(repositorio_mock, _servicio_alertas())

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


@pytest.mark.unit
class TestGenerarAlertasSlaTramos:
    """Tramos de recordatorio: 100% al vencer y luego cada 30% (130, 160, ...)."""

    def _crear_una(self, repositorio_mock, dias_transcurridos, dias_limite=10, **kwargs):
        proceso = crear_proceso_alertable_sla_mock(
            id_proceso_comercial=42,
            dias_transcurridos=dias_transcurridos,
            dias_limite=dias_limite,
            rut_ej_comercial="11111111-1",
            ahora=AHORA_REF,
            **kwargs,
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        return creadas[0]

    @pytest.mark.parametrize(
        ("dias_transcurridos", "tramo_esperado"),
        [
            (11, 100),    # 110% del plazo: primer aviso de vencimiento
            (12.9, 100),  # 129%: todavía en el tramo 100
            (13, 130),    # 130%: primer recordatorio
            (15.9, 130),  # 159%: todavía en el tramo 130
            (16, 160),    # 160%: segundo recordatorio
            (25, 250),    # 250%: sin rellenar los tramos intermedios
        ],
    )
    def test_tramo_segun_porcentaje_consumido(
        self, repositorio_mock, dias_transcurridos, tramo_esperado
    ):
        notificacion = self._crear_una(repositorio_mock, dias_transcurridos)

        assert notificacion.codigo_tipo == "SLA_VENCIDO"
        assert notificacion.nivel == "CRITICO"
        assert notificacion.dedupe_key == (
            f"SLA_VENCIDO@{tramo_esperado}:42:CONTACTO_INICIAL:11111111-1"
        )

    def test_no_genera_alertas_de_los_tramos_saltados(self, repositorio_mock):
        # 250% de una sola vez (p. ej. el scheduler estuvo caído): solo se
        # registra la alerta del tramo actual, sin rellenar 130/160/190/220.
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=25, dias_limite=10, ahora=AHORA_REF
        )
        uc = _use_case(repositorio_mock, proceso)

        creadas = uc.ejecutar(ahora=AHORA_REF)

        assert len(creadas) == 1
        assert repositorio_mock.registrar.call_count == 1

    def test_tramo_70_conserva_su_dedupe_key(self, repositorio_mock):
        notificacion = self._crear_una(repositorio_mock, 7)

        assert notificacion.codigo_tipo == "SLA_POR_VENCER"
        assert notificacion.dedupe_key == "SLA_POR_VENCER@70:42:CONTACTO_INICIAL:11111111-1"

    def test_primer_vencido_conserva_el_texto_original(self, repositorio_mock):
        # Tramo 100: el texto no menciona porcentajes.
        notificacion = self._crear_una(repositorio_mock, 11)

        assert notificacion.titulo == "Oportunidad fuera de plazo en Contacto Inicial"
        assert "(+1 día de atraso)" in notificacion.mensaje
        assert "% del plazo" not in notificacion.mensaje

    def test_recordatorio_indica_porcentaje_consumido_y_atraso(self, repositorio_mock):
        # 13 de 10 días -> 130% consumido, 3 días de atraso.  El mensaje
        # muestra el consumo real, no el tramo del recordatorio.
        notificacion = self._crear_una(repositorio_mock, 13)

        assert notificacion.titulo == "Oportunidad sigue fuera de plazo en Contacto Inicial"
        assert "(va por el 130% del plazo, +3 días de atraso)" in notificacion.mensaje

    @pytest.mark.parametrize(
        ("dias_transcurridos", "porcentaje_esperado"),
        [
            (6.088, 609),  # 608.8% -> entero half-up, como toFixed() del panel
            (6.083, 608),  # 608.3%
            (1.3, 130),    # 130.0%
        ],
    )
    def test_recordatorio_redondea_el_porcentaje_a_entero(
        self, repositorio_mock, dias_transcurridos, porcentaje_esperado
    ):
        notificacion = self._crear_una(repositorio_mock, dias_transcurridos, dias_limite=1)

        assert f"va por el {porcentaje_esperado}% del plazo" in notificacion.mensaje

    def test_recordatorio_no_muestra_el_tramo(self, repositorio_mock):
        # 6.088 días de 1 día -> 608.8% consumido, tramo 580: el tramo es el
        # hito interno del recordatorio y no debe aparecer en el mensaje.
        notificacion = self._crear_una(repositorio_mock, 6.088, dias_limite=1)

        assert "580" not in notificacion.mensaje

    def test_recordatorio_mantiene_la_accion_requerida(self, repositorio_mock):
        notificacion = self._crear_una(
            repositorio_mock, 13, accion_requerida="cargar cotizaciones"
        )

        assert "— falta cargar cotizaciones" in notificacion.mensaje

    def test_tramo_nuevo_marca_leidas_las_alertas_sla_anteriores(self, repositorio_mock):
        # Tramo 130: el aviso de "próximo a vencer" y los tramos menores
        # quedan superados por la alerta nueva.
        proceso = crear_proceso_alertable_sla_mock(
            id_proceso_comercial=42,
            dias_transcurridos=13,
            dias_limite=10,
            rut_ej_comercial="11111111-1",
            ahora=AHORA_REF,
        )
        servicio = _servicio_alertas(marcados=["11111111-1"])
        uc = _use_case(repositorio_mock, proceso, servicio_alertas=servicio)

        uc.ejecutar(ahora=AHORA_REF)

        servicio.marcar_leidas_sla_anteriores.assert_called_once_with(
            42, {"SLA_VENCIDO@130:42:CONTACTO_INICIAL:11111111-1"}, AHORA_REF
        )

    def test_excluye_del_marcado_las_claves_de_todos_los_destinatarios(self, repositorio_mock):
        # Fan-out a dos gerentes: ambas claves del tramo actual quedan fuera
        # del marcado de leídas.
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=13,
            dias_limite=10,
            rol_responsable_siguiente="GERENTE_COMERCIAL",
            ahora=AHORA_REF,
        )
        repositorio_mock.obtener_ruts_por_roles.return_value = {
            "GERENTE_COMERCIAL": ["33333333-3", "44444444-4"],
        }
        servicio = _servicio_alertas()
        uc = _use_case(repositorio_mock, proceso, servicio_alertas=servicio)

        uc.ejecutar(ahora=AHORA_REF)

        servicio.marcar_leidas_sla_anteriores.assert_called_once_with(
            1,
            {
                "SLA_VENCIDO@130:1:CONTACTO_INICIAL:33333333-3",
                "SLA_VENCIDO@130:1:CONTACTO_INICIAL:44444444-4",
            },
            AHORA_REF,
        )


@pytest.mark.unit
class TestResolverEscalonesSla:

    def test_vencido_marca_leidas_las_alertas_anteriores_del_proceso(self, repositorio_mock):
        # 11 de 10 días -> SLA_VENCIDO: el aviso de "próximo a vencer" ya no aplica.
        proceso = crear_proceso_alertable_sla_mock(
            id_proceso_comercial=42, dias_transcurridos=11, dias_limite=10, ahora=AHORA_REF
        )
        servicio = _servicio_alertas()
        uc = _use_case(repositorio_mock, proceso, servicio_alertas=servicio)

        uc.ejecutar(ahora=AHORA_REF)

        servicio.marcar_leidas_sla_anteriores.assert_called_once_with(
            42, {"SLA_VENCIDO@100:42:CONTACTO_INICIAL:11111111-1"}, AHORA_REF
        )

    def test_por_vencer_no_resuelve_nada(self, repositorio_mock):
        # 7 de 10 días -> SLA_POR_VENCER: no hay escalón inferior que resolver.
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=7, dias_limite=10, ahora=AHORA_REF
        )
        servicio = _servicio_alertas()
        uc = _use_case(repositorio_mock, proceso, servicio_alertas=servicio)

        uc.ejecutar(ahora=AHORA_REF)

        servicio.marcar_leidas_sla_anteriores.assert_not_called()

    def test_sin_alerta_no_resuelve_nada(self, repositorio_mock):
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=6, dias_limite=10, ahora=AHORA_REF
        )
        servicio = _servicio_alertas()
        uc = _use_case(repositorio_mock, proceso, servicio_alertas=servicio)

        uc.ejecutar(ahora=AHORA_REF)

        servicio.marcar_leidas_sla_anteriores.assert_not_called()

    def test_publica_los_destinatarios_de_las_alertas_resueltas(self, repositorio_mock):
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=11, dias_limite=10, ahora=AHORA_REF
        )
        servicio = _servicio_alertas(marcados=['11111111-1', '22222222-2'])
        uc = _use_case(
            repositorio_mock, proceso, registrar_retorno=False, servicio_alertas=servicio
        )

        with patch.object(hub, 'publicar_desde_hilo') as publicar:
            uc.ejecutar(ahora=AHORA_REF)

        publicar.assert_called_once_with(
            ['11111111-1', '22222222-2'],
            {
                'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS,
                'motivo': 'alertas_leidas_cambio_estado',
            },
        )

    def test_vencido_sin_alertas_resueltas_no_publica(self, repositorio_mock):
        proceso = crear_proceso_alertable_sla_mock(
            dias_transcurridos=11, dias_limite=10, ahora=AHORA_REF
        )
        servicio = _servicio_alertas()
        uc = _use_case(
            repositorio_mock, proceso, registrar_retorno=False, servicio_alertas=servicio
        )

        with patch.object(hub, 'publicar_desde_hilo') as publicar:
            uc.ejecutar(ahora=AHORA_REF)

        publicar.assert_not_called()
