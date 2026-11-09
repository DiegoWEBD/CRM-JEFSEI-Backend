from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.proceso_comercial.use_cases.crear_proceso_comercial import (
    CrearProcesoComercialUseCase,
)
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.historial_estado.historial_estado_proceso_comercial import (
    HistorialEstadoProcesoComercial,
)
from app.dominio.historial_estado.repositorio_historial_estado_procesos_comerciales import (
    RepositorioHistorialEstadoProcesosComerciales,
)
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import (
    RepositorioProcesosComerciales,
)
from app.dominio.producto.repositorio_producto import RepositorioProducto
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from tests.factories.producto_factory import crear_producto_mock
from tests.factories.usuario_factory import crear_usuario_mock


def _use_case(prospecto_existe=True, autorizado=True, producto_existe=True):
    prospecto = MagicMock(id=1, nombre_riesgo='Riesgo Test')
    prospecto.ejecutivo_comercial_asignado = crear_usuario_mock(rut='22222222-2')
    prospecto.ejecutivo_evaluacion_asignado = crear_usuario_mock(rut='33333333-3')

    repo_prospectos = MagicMock(spec=RepositorioProspectos)
    repo_prospectos.buscar.return_value = prospecto if prospecto_existe else None

    repo_productos = MagicMock(spec=RepositorioProducto)
    repo_productos.obtener_por_codigo.return_value = (
        crear_producto_mock() if producto_existe else None
    )

    repo_procesos = MagicMock(spec=RepositorioProcesosComerciales)
    repo_procesos.guardar.side_effect = lambda proceso, es_nuevo=False: proceso

    repo_historial = MagicMock(spec=RepositorioHistorialEstadoProcesosComerciales)

    authorization_service = MagicMock(spec=AuthorizationService)
    authorization_service.usuario_puede_crear_proceso_comercial.return_value = autorizado

    uc = CrearProcesoComercialUseCase(
        authorization_service,
        repo_procesos,
        repo_prospectos,
        repo_productos,
        repo_historial,
    )
    return uc, repo_prospectos, repo_productos, repo_procesos, repo_historial


@pytest.mark.unit
class TestCrearProcesoComercial:

    def test_crea_el_proceso_en_oportunidad_creada(self):
        uc, repo_prospectos, repo_productos, repo_procesos, _ = _use_case()
        prospecto = repo_prospectos.buscar.return_value

        proceso = uc.ejecutar(tipo='PROD-1', id_prospecto=1, usuario=crear_usuario_mock())

        repo_procesos.guardar.assert_called_once_with(proceso, es_nuevo=True)
        assert proceso.estado_actual.codigo == 'OPORTUNIDAD_CREADA'
        assert proceso.id_prospecto == 1
        assert proceso.nombre_cliente == prospecto.nombre_riesgo
        assert proceso.producto is repo_productos.obtener_por_codigo.return_value
        assert proceso.ejecutivo_comercial == prospecto.ejecutivo_comercial_asignado
        assert proceso.ejecutivo_evaluacion == prospecto.ejecutivo_evaluacion_asignado
        assert proceso.cerrado is False
        assert proceso.renovacion is False
        assert isinstance(proceso.fecha_apertura, datetime)

    def test_registra_historial_oportunidad_creada(self):
        uc, _, _, _, repo_historial = _use_case()
        usuario = crear_usuario_mock(rut='99999999-9')

        proceso = uc.ejecutar(tipo='PROD-1', id_prospecto=1, usuario=usuario)

        repo_historial.registrar.assert_called_once()
        historial = repo_historial.registrar.call_args.args[0]
        assert isinstance(historial, HistorialEstadoProcesoComercial)
        assert historial.id_proceso_comercial == proceso.id
        assert historial.codigo_estado == 'OPORTUNIDAD_CREADA'
        assert historial.rut_registrado_por == usuario.rut
        assert historial.fecha == proceso.fecha_apertura

    def test_producto_inexistente_lanza_excepcion(self):
        uc, _, _, repo_procesos, repo_historial = _use_case(producto_existe=False)

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar(tipo='NOEXISTE', id_prospecto=1, usuario=crear_usuario_mock())

        repo_procesos.guardar.assert_not_called()
        repo_historial.registrar.assert_not_called()

    def test_prospecto_inexistente_no_crea(self):
        uc, _, repo_productos, repo_procesos, repo_historial = _use_case(prospecto_existe=False)

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar(tipo='PROD-1', id_prospecto=99, usuario=crear_usuario_mock())

        repo_productos.obtener_por_codigo.assert_not_called()
        repo_procesos.guardar.assert_not_called()
        repo_historial.registrar.assert_not_called()

    def test_no_autorizado_no_crea(self):
        uc, _, _, repo_procesos, repo_historial = _use_case(autorizado=False)

        with pytest.raises(UsuarioNoAutorizadoException):
            uc.ejecutar(tipo='PROD-1', id_prospecto=1, usuario=crear_usuario_mock())

        repo_procesos.guardar.assert_not_called()
        repo_historial.registrar.assert_not_called()
