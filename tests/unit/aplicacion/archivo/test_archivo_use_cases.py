import pytest
from unittest.mock import MagicMock

from app.aplicacion.archivo.servicios.servicio_archivos import ServicioArchivos
from app.aplicacion.archivo.use_cases.eliminar_archivo import EliminarArchivoUseCase
from app.aplicacion.archivo.use_cases.obtener_archivo_por_id import ObtenerArchivoPorIdUseCase
from app.aplicacion.archivo.use_cases.obtener_archivos_prospecto import ObtenerArchivosProspectoUseCase
from app.aplicacion.archivo.use_cases.subir_archivo import SubirArchivoUseCase
from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.archivo.repositorio_archivos import RepositorioArchivos
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from tests.factories.archivo_factory import crear_archivo_mock
from tests.factories.prospecto_factory import crear_prospecto_mock
from tests.factories.usuario_factory import crear_usuario_mock


@pytest.fixture
def repositorio_archivos_mock():
    mock = MagicMock(spec=RepositorioArchivos)
    mock.obtener_por_id.return_value = crear_archivo_mock()
    mock.listar_por_prospecto.return_value = [crear_archivo_mock()]
    mock.existe_nombre_original.return_value = False
    mock.insertar.return_value = crear_archivo_mock()
    return mock


@pytest.fixture
def repositorio_prospectos_mock():
    mock = MagicMock(spec=RepositorioProspectos)
    mock.buscar.return_value = crear_prospecto_mock(id=7)
    return mock


@pytest.fixture
def authorization_service_mock():
    return MagicMock(spec=AuthorizationService)


@pytest.fixture
def servicio_archivos_mock():
    return MagicMock(spec=ServicioArchivos)


@pytest.fixture
def usuario():
    return crear_usuario_mock(rut='11111111-1')


@pytest.mark.unit
class TestSubirArchivoUseCase:

    def _use_case(self, ra, rp, az, sa):
        return SubirArchivoUseCase(ra, rp, az, sa)

    def test_prospecto_inexistente_retorna_404(
        self, repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock, servicio_archivos_mock, usuario,
    ):
        repositorio_prospectos_mock.buscar.return_value = None
        use_case = self._use_case(repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock, servicio_archivos_mock)

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(usuario=usuario, id_prospecto=7, nombre_almacenado='x.pdf',
                              nombre_original='x.pdf', tipo_contenido='application/pdf',
                              tamano_bytes=1, contenido=b'a')

        repositorio_archivos_mock.insertar.assert_not_called()

    def test_solo_permiso_de_ver_no_permite_subir(
        self, repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock, servicio_archivos_mock, usuario,
    ):
        # Re-chequeo con la familia ADMINISTRAR: usuario_puede_administrar_archivos_prospecto False.
        authorization_service_mock.usuario_puede_administrar_archivos_prospecto.return_value = False
        use_case = self._use_case(repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock, servicio_archivos_mock)

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(usuario=usuario, id_prospecto=7, nombre_almacenado='x.pdf',
                              nombre_original='x.pdf', tipo_contenido='application/pdf',
                              tamano_bytes=1, contenido=b'a')

        authorization_service_mock.usuario_puede_administrar_archivos_prospecto.assert_called_once_with(usuario, 7)
        servicio_archivos_mock.guardar.assert_not_called()

    def test_nombre_duplicado_retorna_conflicto(
        self, repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock, servicio_archivos_mock, usuario,
    ):
        authorization_service_mock.usuario_puede_administrar_archivos_prospecto.return_value = True
        repositorio_archivos_mock.existe_nombre_original.return_value = True
        use_case = self._use_case(repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock, servicio_archivos_mock)

        with pytest.raises(RecursoYaExisteException):
            use_case.ejecutar(usuario=usuario, id_prospecto=7, nombre_almacenado='x.pdf',
                              nombre_original='x.pdf', tipo_contenido='application/pdf',
                              tamano_bytes=1, contenido=b'a')

    def test_con_autorizacion_sube_con_rut_del_usuario(
        self, repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock, servicio_archivos_mock, usuario,
    ):
        authorization_service_mock.usuario_puede_administrar_archivos_prospecto.return_value = True
        use_case = self._use_case(repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock, servicio_archivos_mock)

        use_case.ejecutar(usuario=usuario, id_prospecto=7, nombre_almacenado='x.pdf',
                          nombre_original='x.pdf', tipo_contenido='application/pdf',
                          tamano_bytes=1, contenido=b'a')

        assert repositorio_archivos_mock.insertar.call_args.kwargs['rut_subido_por'] == '11111111-1'
        servicio_archivos_mock.guardar.assert_called_once()


@pytest.mark.unit
class TestEliminarArchivoUseCase:

    def test_solo_permiso_de_ver_no_permite_eliminar(
        self, repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock, servicio_archivos_mock, usuario,
    ):
        # Fix semántico: "ver" el prospecto ya no habilita borrar archivos.
        authorization_service_mock.usuario_puede_administrar_archivos_prospecto.return_value = False
        use_case = EliminarArchivoUseCase(repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock, servicio_archivos_mock)

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(usuario=usuario, id_archivo=1, id_prospecto=7)

        repositorio_archivos_mock.eliminar.assert_not_called()

    def test_archivo_inexistente_retorna_404(
        self, repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock, servicio_archivos_mock, usuario,
    ):
        authorization_service_mock.usuario_puede_administrar_archivos_prospecto.return_value = True
        repositorio_archivos_mock.obtener_por_id.return_value = None
        use_case = EliminarArchivoUseCase(repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock, servicio_archivos_mock)

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(usuario=usuario, id_archivo=999, id_prospecto=7)

    def test_archivo_de_otro_prospecto_retorna_404(
        self, repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock, servicio_archivos_mock, usuario,
    ):
        authorization_service_mock.usuario_puede_administrar_archivos_prospecto.return_value = True
        repositorio_archivos_mock.obtener_por_id.return_value = crear_archivo_mock(id_prospecto=99)
        use_case = EliminarArchivoUseCase(repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock, servicio_archivos_mock)

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(usuario=usuario, id_archivo=1, id_prospecto=7)

        repositorio_archivos_mock.eliminar.assert_not_called()

    def test_con_autorizacion_elimina(
        self, repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock, servicio_archivos_mock, usuario,
    ):
        authorization_service_mock.usuario_puede_administrar_archivos_prospecto.return_value = True
        use_case = EliminarArchivoUseCase(repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock, servicio_archivos_mock)

        use_case.ejecutar(usuario=usuario, id_archivo=1, id_prospecto=7)

        repositorio_archivos_mock.eliminar.assert_called_once_with(1)
        servicio_archivos_mock.eliminar.assert_called_once()


@pytest.mark.unit
class TestObtenerArchivoPorIdUseCase:

    def test_sin_permiso_ver_retorna_403(
        self, repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock, usuario,
    ):
        authorization_service_mock.usuario_puede_ver_archivos_prospecto.return_value = False
        use_case = ObtenerArchivoPorIdUseCase(repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock)

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(usuario=usuario, id_archivo=1, id_prospecto=7)

    def test_archivo_de_otro_prospecto_retorna_404(
        self, repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock, usuario,
    ):
        authorization_service_mock.usuario_puede_ver_archivos_prospecto.return_value = True
        repositorio_archivos_mock.obtener_por_id.return_value = crear_archivo_mock(id_prospecto=99)
        use_case = ObtenerArchivoPorIdUseCase(repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock)

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(usuario=usuario, id_archivo=1, id_prospecto=7)

    def test_con_permiso_retorna_archivo(
        self, repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock, usuario,
    ):
        authorization_service_mock.usuario_puede_ver_archivos_prospecto.return_value = True
        use_case = ObtenerArchivoPorIdUseCase(repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock)

        resultado = use_case.ejecutar(usuario=usuario, id_archivo=1, id_prospecto=7)

        assert resultado.id == 1


@pytest.mark.unit
class TestObtenerArchivosProspectoUseCase:

    def test_sin_permiso_ver_retorna_403(
        self, repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock, usuario,
    ):
        authorization_service_mock.usuario_puede_ver_archivos_prospecto.return_value = False
        use_case = ObtenerArchivosProspectoUseCase(repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock)

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(usuario=usuario, id_prospecto=7)

        repositorio_archivos_mock.listar_por_prospecto.assert_not_called()

    def test_prospecto_inexistente_retorna_404(
        self, repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock, usuario,
    ):
        repositorio_prospectos_mock.buscar.return_value = None
        use_case = ObtenerArchivosProspectoUseCase(repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock)

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(usuario=usuario, id_prospecto=7)

    def test_con_permiso_lista(
        self, repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock, usuario,
    ):
        authorization_service_mock.usuario_puede_ver_archivos_prospecto.return_value = True
        use_case = ObtenerArchivosProspectoUseCase(repositorio_archivos_mock, repositorio_prospectos_mock, authorization_service_mock)

        resultado = use_case.ejecutar(usuario=usuario, id_prospecto=7)

        assert len(resultado) == 1
