from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.notificacion.use_cases.refrescar_alertas_renovacion import (
    RefrescarAlertasRenovacionUseCase,
)
from app.aplicacion.prospecto.use_cases.asignar_ejecutivo_renovacion import (
    AsignarEjecutivoRenovacionUseCase,
)
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import TIPO_ASIGNACION, TIPO_DESASIGNACION
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales

MODULO = 'app.aplicacion.prospecto.use_cases.asignar_ejecutivo_renovacion'


def _prospecto_mock(id=1, id_cliente=5, renovacion_previa=None, nombre_riesgo='Cliente Test'):
    p = MagicMock()
    p.id = id
    p.id_cliente = id_cliente
    p.nombre_riesgo = nombre_riesgo
    p.ejecutivo_renovacion_asignado = renovacion_previa
    return p


def _use_case(prospecto, rut_nuevo=None):
    repo_prospectos = MagicMock()
    repo_prospectos.buscar_cliente.return_value = prospecto
    repo_usuarios = MagicMock()
    if rut_nuevo is not None:
        repo_usuarios.buscar.return_value = MagicMock(rut=rut_nuevo)
    repo_notificaciones = MagicMock(spec=RepositorioNotificaciones)
    refrescar = MagicMock(spec=RefrescarAlertasRenovacionUseCase)
    repo_procesos = MagicMock(spec=RepositorioProcesosComerciales)
    repo_procesos.obtener_procesos_comerciales.return_value = []
    uc = AsignarEjecutivoRenovacionUseCase(
        repo_prospectos, repo_usuarios, repo_notificaciones, refrescar, repo_procesos
    )
    return uc, repo_prospectos, repo_notificaciones, refrescar, repo_procesos


@pytest.mark.unit
class TestAsignarEjecutivoRenovacion:

    def test_cliente_no_encontrado_lanza_excepcion(self):
        repo_prospectos = MagicMock()
        repo_prospectos.buscar_cliente.return_value = None
        uc = AsignarEjecutivoRenovacionUseCase(
            repo_prospectos, MagicMock(), MagicMock(), MagicMock(), MagicMock()
        )

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar(id_cliente=99, rut_ej_renovacion='11111111-1', asignado_por=MagicMock())

    def test_sin_cliente_asociado_lanza_excepcion(self):
        prospecto = _prospecto_mock(id_cliente=None)
        uc, repo_prospectos, repo_notificaciones, refrescar, _ = _use_case(
            prospecto, rut_nuevo='11111111-1'
        )

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar(id_cliente=5, rut_ej_renovacion='11111111-1', asignado_por=MagicMock())

        repo_prospectos.actualizar_prospecto.assert_not_called()
        repo_notificaciones.registrar.assert_not_called()
        refrescar.ejecutar.assert_not_called()


@pytest.mark.unit
@patch(f'{MODULO}.hub')
class TestAsignarEjecutivoRenovacionNotificaciones:

    def test_crea_notificacion_asignacion_cliente(self, mock_hub):
        prospecto = _prospecto_mock(renovacion_previa=None)
        uc, _, repo_notificaciones, *_ = _use_case(prospecto, rut_nuevo='11111111-1')

        uc.ejecutar(id_cliente=5, rut_ej_renovacion='11111111-1', asignado_por=MagicMock())

        repo_notificaciones.registrar.assert_called_once()
        notificacion = repo_notificaciones.registrar.call_args.args[0]
        assert notificacion.codigo_tipo == TIPO_ASIGNACION
        assert notificacion.rut_usuario == '11111111-1'
        assert notificacion.nivel == 'INFO'
        assert notificacion.leible is True
        assert notificacion.titulo == 'Asignación de renovación'
        assert notificacion.mensaje == (
            'Se le ha asignado la renovación del cliente Cliente Test.'
        )
        assert notificacion.entidad_tipo == 'CLIENTE'
        assert notificacion.entidad_id == 5
        assert notificacion.id_prospecto == 1
        assert notificacion.dedupe_key.startswith(f'{TIPO_ASIGNACION}:CLIENTE:5:renovación:')

    def test_crea_desasignacion_solo_si_cambio(self, mock_hub):
        prospecto = _prospecto_mock(renovacion_previa=MagicMock(rut='33333333-3'))
        uc, _, repo_notificaciones, *_ = _use_case(prospecto, rut_nuevo='11111111-1')

        uc.ejecutar(id_cliente=5, rut_ej_renovacion='11111111-1', asignado_por=MagicMock())

        tipos = [c.args[0].codigo_tipo for c in repo_notificaciones.registrar.call_args_list]
        assert tipos == [TIPO_ASIGNACION, TIPO_DESASIGNACION]
        desasignacion = repo_notificaciones.registrar.call_args_list[1].args[0]
        assert desasignacion.rut_usuario == '33333333-3'
        assert desasignacion.dedupe_key.startswith(f'{TIPO_DESASIGNACION}:CLIENTE:5:renovación:')

    def test_no_repite_asignacion_si_el_rut_no_cambia(self, mock_hub):
        prospecto = _prospecto_mock(renovacion_previa=MagicMock(rut='11111111-1'))
        uc, _, repo_notificaciones, *_ = _use_case(prospecto, rut_nuevo='11111111-1')

        uc.ejecutar(id_cliente=5, rut_ej_renovacion='11111111-1', asignado_por=MagicMock())

        repo_notificaciones.registrar.assert_not_called()

    def test_sigue_notificando_asignacion_y_desasignacion(self, mock_hub):
        prospecto = _prospecto_mock(renovacion_previa=MagicMock(rut='33333333-3'))
        uc, *_ = _use_case(prospecto, rut_nuevo='11111111-1')

        uc.ejecutar(id_cliente=5, rut_ej_renovacion='11111111-1', asignado_por=MagicMock())

        motivos = [c.args[1]['motivo'] for c in mock_hub.publicar_desde_hilo.call_args_list]
        assert 'asignacion_ejecutivo' in motivos
        assert 'desasignacion_ejecutivo' in motivos


@pytest.mark.unit
class TestAsignarEjecutivoRenovacionRefrescoAlertas:

    def test_con_cambio_de_rut_refresca_alertas_de_renovacion(self):
        prospecto = _prospecto_mock(renovacion_previa=MagicMock(rut='33333333-3'))
        uc, repo_prospectos, _, refrescar, _ = _use_case(prospecto, rut_nuevo='11111111-1')

        uc.ejecutar(id_cliente=5, rut_ej_renovacion='11111111-1', asignado_por=MagicMock())

        # Tras guardar la asignación, se eliminan las alertas del anterior y se
        # re-evalúan al tiro para crear las del nuevo destinatario.
        repo_prospectos.actualizar_prospecto.assert_called_once_with(prospecto)
        refrescar.ejecutar.assert_called_once_with(5)

    def test_sin_cambio_de_rut_no_refresca(self):
        prospecto = _prospecto_mock(renovacion_previa=MagicMock(rut='11111111-1'))
        uc, _, _, refrescar, _ = _use_case(prospecto, rut_nuevo='11111111-1')

        uc.ejecutar(id_cliente=5, rut_ej_renovacion='11111111-1', asignado_por=MagicMock())

        refrescar.ejecutar.assert_not_called()

    def test_desasignacion_tambien_refresca(self):
        prospecto = _prospecto_mock(renovacion_previa=MagicMock(rut='33333333-3'))
        uc, _, _, refrescar, _ = _use_case(prospecto, rut_nuevo=None)

        uc.ejecutar(id_cliente=5, rut_ej_renovacion=None, asignado_por=MagicMock())

        refrescar.ejecutar.assert_called_once_with(5)


@pytest.mark.unit
class TestAsignarEjecutivoRenovacionProcesosAbiertos:

    def test_reasigna_al_ejecutivo_en_procesos_de_renovacion_abiertos(self):
        prospecto = _prospecto_mock(renovacion_previa=None)
        uc, _, _, _, repo_procesos = _use_case(prospecto, rut_nuevo='11111111-1')
        proceso = MagicMock()
        repo_procesos.obtener_procesos_comerciales.return_value = [proceso]

        uc.ejecutar(id_cliente=5, rut_ej_renovacion='11111111-1', asignado_por=MagicMock())

        repo_procesos.obtener_procesos_comerciales.assert_called_once_with(
            id_prospecto=1,
            abiertos=True,
            renovaciones=True,
        )
        assert proceso.ejecutivo_renovacion == prospecto.ejecutivo_renovacion_asignado
        repo_procesos.actualizar.assert_called_once_with(proceso)

    def test_sin_cambio_de_rut_no_toca_los_procesos(self):
        prospecto = _prospecto_mock(renovacion_previa=MagicMock(rut='11111111-1'))
        uc, _, _, _, repo_procesos = _use_case(prospecto, rut_nuevo='11111111-1')

        uc.ejecutar(id_cliente=5, rut_ej_renovacion='11111111-1', asignado_por=MagicMock())

        repo_procesos.obtener_procesos_comerciales.assert_not_called()
        repo_procesos.actualizar.assert_not_called()
