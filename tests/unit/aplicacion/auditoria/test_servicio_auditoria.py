from unittest.mock import MagicMock

import pytest

from app.aplicacion.auditoria.servicio_auditoria import ServicioAuditoria
from app.dominio.auditoria.eventos_auditoria import (
    CategoriaAuditoria,
    EventoAuditoria,
    ResultadoAuditoria,
)
from app.dominio.auditoria.repositorio_auditoria import RepositorioAuditoria
from tests.factories.auditoria_factory import crear_contexto_peticion_mock


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioAuditoria)


@pytest.fixture
def servicio(repositorio_mock):
    return ServicioAuditoria(repositorio_mock)


@pytest.mark.unit
class TestServicioAuditoria:

    def test_registrar_autenticacion_construye_registro(self, servicio, repositorio_mock):
        contexto = crear_contexto_peticion_mock()

        servicio.registrar_autenticacion(
            evento=EventoAuditoria.LOGIN_EXITOSO,
            resultado=ResultadoAuditoria.EXITO,
            contexto=contexto,
            rut_usuario="12345678-9",
            nombre_usuario="Juan Perez",
        )

        registro = repositorio_mock.registrar.call_args[0][0]
        assert registro.categoria == CategoriaAuditoria.AUTENTICACION
        assert registro.evento == EventoAuditoria.LOGIN_EXITOSO
        assert registro.resultado == ResultadoAuditoria.EXITO
        assert registro.rut_usuario == "12345678-9"
        assert registro.nombre_usuario == "Juan Perez"
        assert registro.ip_origen == contexto.ip_origen
        assert registro.user_agent == contexto.user_agent
        assert registro.id_peticion == contexto.id_peticion

    def test_registrar_autenticacion_fallida_guarda_rut_intentado(self, servicio, repositorio_mock):
        contexto = crear_contexto_peticion_mock()

        servicio.registrar_autenticacion(
            evento=EventoAuditoria.LOGIN_FALLIDO,
            resultado=ResultadoAuditoria.FALLIDO,
            contexto=contexto,
            rut_usuario="99999999-9",
            detalle="Credenciales invalidas",
        )

        registro = repositorio_mock.registrar.call_args[0][0]
        assert registro.evento == EventoAuditoria.LOGIN_FALLIDO
        assert registro.resultado == ResultadoAuditoria.FALLIDO
        assert registro.rut_usuario == "99999999-9"
        assert registro.detalle == "Credenciales invalidas"

    def test_registrar_accion_negocio_construye_registro(self, servicio, repositorio_mock):
        contexto = crear_contexto_peticion_mock()

        servicio.registrar_accion_negocio(
            evento=EventoAuditoria.CREAR,
            resultado=ResultadoAuditoria.EXITO,
            contexto=contexto,
            estado_http=201,
            rut_usuario="12345678-9",
            nombre_usuario="Juan Perez",
            metodo="POST",
            ruta="/prospectos/",
            entidad_tipo="prospectos",
            entidad_id=None,
            duracion_ms=15,
        )

        registro = repositorio_mock.registrar.call_args[0][0]
        assert registro.categoria == CategoriaAuditoria.ACCION_NEGOCIO
        assert registro.evento == EventoAuditoria.CREAR
        assert registro.estado_http == 201
        assert registro.metodo == "POST"
        assert registro.ruta == "/prospectos/"
        assert registro.entidad_tipo == "prospectos"
        assert registro.duracion_ms == 15

    def test_registrar_accion_negocio_guarda_detalle(self, servicio, repositorio_mock):
        contexto = crear_contexto_peticion_mock()

        servicio.registrar_accion_negocio(
            evento=EventoAuditoria.EJECUTAR_ACCION,
            resultado=ResultadoAuditoria.EXITO,
            contexto=contexto,
            detalle="El usuario 12345678-9 ha asignado la gestión comercial",
        )

        registro = repositorio_mock.registrar.call_args[0][0]
        assert registro.detalle == "El usuario 12345678-9 ha asignado la gestión comercial"

    def test_fallo_del_repositorio_no_propaga_excepcion(self, repositorio_mock):
        repositorio_mock.registrar.side_effect = RuntimeError("db caida")
        servicio = ServicioAuditoria(repositorio_mock)
        contexto = crear_contexto_peticion_mock()

        servicio.registrar_autenticacion(
            evento=EventoAuditoria.LOGOUT,
            resultado=ResultadoAuditoria.EXITO,
            contexto=contexto,
            rut_usuario="12345678-9",
        )

        assert repositorio_mock.registrar.called
