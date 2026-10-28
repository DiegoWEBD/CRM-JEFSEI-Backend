from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.notificacion.use_cases.generar_alerta_renovacion_poliza import (
    GenerarAlertaRenovacionPolizaUseCase,
)
from app.aplicacion.notificacion.use_cases.refrescar_alertas_renovacion import (
    RefrescarAlertasRenovacionUseCase,
)
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from tests.factories.notificacion_factory import (
    AHORA_REF,
    crear_notificacion_mock,
    crear_poliza_alertable_renovacion_mock,
)

MODULO = 'app.aplicacion.notificacion.use_cases.refrescar_alertas_renovacion'


def _use_case(polizas, *, destinatarios=None, alertas_evaluadas=None):
    repo = MagicMock(spec=RepositorioNotificaciones)
    repo.obtener_polizas_alertables_renovacion.return_value = list(polizas)
    repo.buscar_notificaciones_por_poliza.return_value = []
    repo.registrar.return_value = True
    generar = MagicMock(spec=GenerarAlertaRenovacionPolizaUseCase)
    generar.resolver_destinatarios.return_value = list(destinatarios or [])
    generar.evaluar.return_value = list(alertas_evaluadas or [])
    return RefrescarAlertasRenovacionUseCase(repo, generar), repo, generar


def _alerta_poliza(rut_usuario, numero_poliza='POL-001', **kwargs):
    return crear_notificacion_mock(
        id=kwargs.pop('id', 1),
        rut_usuario=rut_usuario,
        numero_poliza=numero_poliza,
        **kwargs,
    )


@pytest.mark.unit
@patch(f'{MODULO}.hub')
class TestRefrescarAlertasRenovacion:

    def test_elimina_las_no_leidas_de_quien_ya_no_es_destinatario(self, hub_mock):
        poliza = crear_poliza_alertable_renovacion_mock()
        alerta_viejo = _alerta_poliza('11111111-1', codigo_tipo='RENOVACION_GESTION_PENDIENTE')
        alerta_nuevo = _alerta_poliza('22222222-2', id=2, codigo_tipo='RENOVACION_GESTION_PENDIENTE')
        uc, repo, _ = _use_case([poliza], destinatarios=['22222222-2'])
        repo.buscar_notificaciones_por_poliza.return_value = [alerta_viejo, alerta_nuevo]

        uc.ejecutar(5, AHORA_REF)

        repo.buscar_notificaciones_por_poliza.assert_called_once_with('POL-001')
        repo.eliminar.assert_called_once_with(alerta_viejo)

    def test_re_evalua_y_registra_alertas_nuevas(self, hub_mock):
        """La alerta del nuevo destinatario se crea ahora (no se transfiere)."""
        poliza = crear_poliza_alertable_renovacion_mock()
        alerta_nueva = _alerta_poliza(
            '22222222-2', id=None, codigo_tipo='RENOVACION_GESTION_PENDIENTE'
        )
        uc, repo, generar = _use_case(
            [poliza], destinatarios=['22222222-2'], alertas_evaluadas=[alerta_nueva]
        )

        uc.ejecutar(5, AHORA_REF)

        generar.evaluar.assert_called_once_with(poliza, AHORA_REF)
        repo.registrar.assert_called_once_with(alerta_nueva)

    def test_conserva_las_alertas_de_quien_sigue_siendo_destinatario(self, hub_mock):
        """Al cambiar el ejecutivo, el asistente sigue asignado: sus alertas no
        se eliminan ni se re-crean (la dedupe_key existente evita duplicados)."""
        poliza = crear_poliza_alertable_renovacion_mock(
            rut_ej_renovacion='22222222-2', rut_as_renovacion='33333333-3'
        )
        alerta_viejo = _alerta_poliza('11111111-1', codigo_tipo='RENOVACION_COTIZACION_PENDIENTE')
        alerta_asistente = _alerta_poliza(
            '33333333-3', id=2, codigo_tipo='RENOVACION_COTIZACION_PENDIENTE'
        )
        uc, repo, _ = _use_case(
            [poliza], destinatarios=['22222222-2', '33333333-3'], alertas_evaluadas=[alerta_asistente]
        )
        repo.buscar_notificaciones_por_poliza.return_value = [alerta_viejo, alerta_asistente]
        # La alerta del asistente ya existe: su dedupe_key evita re-crearla.
        repo.registrar.return_value = False

        uc.ejecutar(5, AHORA_REF)

        repo.eliminar.assert_called_once_with(alerta_viejo)
        repo.registrar.assert_called_once_with(alerta_asistente)
        # Solo se refresca el usuario saliente; el asistente no se notifica.
        hub_mock.publicar_desde_hilo.assert_called_once()
        assert set(hub_mock.publicar_desde_hilo.call_args.args[0]) == {'11111111-1'}

    def test_no_toca_alertas_leidas_ni_de_otros_tipos(self, hub_mock):
        poliza = crear_poliza_alertable_renovacion_mock()
        alerta_leida = _alerta_poliza(
            '11111111-1', codigo_tipo='RENOVACION_GESTION_PENDIENTE', leida=True
        )
        alerta_asignacion = _alerta_poliza(
            '11111111-1', id=2, codigo_tipo='ASIGNACION_EJECUTIVO'
        )
        alerta_obsoleta = _alerta_poliza(
            '11111111-1', id=3, codigo_tipo='RENOVACION_POLIZA_VENCIDA'
        )
        uc, repo, _ = _use_case([poliza], destinatarios=['22222222-2'])
        repo.buscar_notificaciones_por_poliza.return_value = [
            alerta_leida,
            alerta_asignacion,
            alerta_obsoleta,
        ]

        uc.ejecutar(5, AHORA_REF)

        repo.eliminar.assert_called_once_with(alerta_obsoleta)

    def test_sin_asignados_conserva_las_del_fan_out_por_rol(self, hub_mock):
        poliza = crear_poliza_alertable_renovacion_mock(
            rut_ej_renovacion=None, rut_as_renovacion=None
        )
        alerta_rol = _alerta_poliza('44444444-4', codigo_tipo='RENOVACION_GESTION_PENDIENTE')
        alerta_viejo = _alerta_poliza(
            '11111111-1', id=2, codigo_tipo='RENOVACION_GESTION_PENDIENTE'
        )
        uc, repo, _ = _use_case([poliza], destinatarios=['44444444-4', '55555555-5'])
        repo.buscar_notificaciones_por_poliza.return_value = [alerta_rol, alerta_viejo]

        uc.ejecutar(5, AHORA_REF)

        repo.eliminar.assert_called_once_with(alerta_viejo)

    def test_publica_el_refresco_a_eliminados_y_creados(self, hub_mock):
        poliza = crear_poliza_alertable_renovacion_mock()
        alerta_viejo = _alerta_poliza('11111111-1', codigo_tipo='RENOVACION_GESTION_PENDIENTE')
        alerta_nueva = _alerta_poliza(
            '22222222-2', id=None, codigo_tipo='RENOVACION_GESTION_PENDIENTE'
        )
        uc, repo, _ = _use_case(
            [poliza], destinatarios=['22222222-2'], alertas_evaluadas=[alerta_nueva]
        )
        repo.buscar_notificaciones_por_poliza.return_value = [alerta_viejo]

        uc.ejecutar(5, AHORA_REF)

        hub_mock.publicar_desde_hilo.assert_called_once()
        destinatarios = set(hub_mock.publicar_desde_hilo.call_args.args[0])
        payload = hub_mock.publicar_desde_hilo.call_args.args[1]
        assert destinatarios == {'11111111-1', '22222222-2'}
        assert payload == {
            'evento': 'notificaciones_actualizadas',
            'motivo': 'alertas_renovacion_actualizadas',
        }

    def test_no_duplica_alertas_ya_registradas(self, hub_mock):
        poliza = crear_poliza_alertable_renovacion_mock()
        alerta = _alerta_poliza(
            '22222222-2', id=None, codigo_tipo='RENOVACION_GESTION_PENDIENTE'
        )
        uc, repo, _ = _use_case([poliza], destinatarios=['22222222-2'], alertas_evaluadas=[alerta])
        repo.registrar.return_value = False

        uc.ejecutar(5, AHORA_REF)

        hub_mock.publicar_desde_hilo.assert_not_called()

    def test_evalua_todas_las_polizas_del_cliente(self, hub_mock):
        polizas = [
            crear_poliza_alertable_renovacion_mock(numero_poliza=f'POL-00{i}')
            for i in range(3)
        ]
        uc, repo, generar = _use_case(polizas)

        uc.ejecutar(5, AHORA_REF)

        repo.obtener_polizas_alertables_renovacion.assert_called_once_with(id_cliente=5)
        assert generar.evaluar.call_count == 3
        assert repo.buscar_notificaciones_por_poliza.call_count == 3

    def test_sin_polizas_no_hace_nada(self, hub_mock):
        uc, repo, generar = _use_case([])

        uc.ejecutar(5, AHORA_REF)

        generar.evaluar.assert_not_called()
        repo.eliminar.assert_not_called()
        repo.registrar.assert_not_called()
        hub_mock.publicar_desde_hilo.assert_not_called()
