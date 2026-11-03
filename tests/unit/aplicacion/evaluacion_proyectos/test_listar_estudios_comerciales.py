from unittest.mock import MagicMock

import pytest

from app.aplicacion.evaluacion_proyectos.use_cases.listar_estudios_comerciales import ListarEstudiosComercialesUseCase
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException

RUT_USUARIO = '12345678-9'

AUSENTE = object()


def _usuario(rut=RUT_USUARIO):
    usuario = MagicMock()
    usuario.rut = rut
    return usuario


def _estudio(id=5):
    estudio = MagicMock()
    estudio.id = id
    estudio.nombre_archivo = f'estudio_comercial_1_{id}.pdf'
    return estudio


def _use_case(solicitud=AUSENTE, puede_ver=True, estudios=None):
    repositorio_solicitudes = MagicMock()
    repositorio_solicitudes.buscar.return_value = MagicMock() if solicitud is AUSENTE else solicitud

    repositorio_estudios = MagicMock()
    repositorio_estudios.listar_por_id_solicitud.return_value = estudios if estudios is not None else []

    authorization_service = MagicMock()
    authorization_service.usuario_puede_ver_estudios_comerciales.return_value = puede_ver

    use_case = ListarEstudiosComercialesUseCase(
        repositorio_solicitudes=repositorio_solicitudes,
        repositorio_estudios=repositorio_estudios,
        authorization_service=authorization_service,
    )

    return use_case, repositorio_solicitudes, repositorio_estudios


@pytest.mark.unit
class TestListarEstudiosComerciales:

    def test_solicitud_no_encontrada(self):
        use_case, _, repositorio_estudios = _use_case(solicitud=None)

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(id_solicitud=99, usuario=_usuario())

        repositorio_estudios.listar_por_id_solicitud.assert_not_called()

    def test_usuario_no_autorizado(self):
        use_case, _, repositorio_estudios = _use_case(puede_ver=False)

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(id_solicitud=1, usuario=_usuario())

        repositorio_estudios.listar_por_id_solicitud.assert_not_called()

    def test_retorna_estudios_de_la_solicitud(self):
        estudios = [_estudio(id=5), _estudio(id=6)]
        use_case, repositorio_solicitudes, repositorio_estudios = _use_case(estudios=estudios)

        resultado = use_case.ejecutar(id_solicitud=1, usuario=_usuario())

        assert resultado == estudios
        repositorio_solicitudes.buscar.assert_called_once_with(1)
        repositorio_estudios.listar_por_id_solicitud.assert_called_once_with(1)
