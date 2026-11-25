import pytest
from unittest.mock import MagicMock
from app.aplicacion.usuario.use_cases.registrar_usuario import RegistrarUsuarioUseCase
from app.aplicacion.usuario.use_cases.obtener_usuario import ObtenerUsuarioUseCase
from app.aplicacion.usuario.use_cases.obtener_usuarios import ObtenerUsuariosUseCase
from app.aplicacion.usuario.use_cases.eliminar_usuario import EliminarUsuarioUseCase
from app.aplicacion.usuario.use_cases.actualizar_usuario import ActualizarUsuarioUseCase
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.aplicacion.auth.authentication_service import AuthenticationService
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from tests.factories.usuario_factory import crear_usuario_mock


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioUsuarios)


@pytest.fixture
def auth_service_mock():
    service = MagicMock(spec=AuthenticationService)
    service.hash_password.return_value = "hashed_password_123"
    return service


@pytest.mark.unit
class TestRegistrarUsuarioUseCase:

    def test_registrar_exitoso(self, repositorio_mock, auth_service_mock):
        repositorio_mock.buscar.return_value = None
        repositorio_mock.existe_correo.return_value = False
        repositorio_mock.existe_telefono.return_value = False
        repositorio_mock.registrar.return_value = True

        uc = RegistrarUsuarioUseCase(repositorio_mock, auth_service_mock)
        resultado = uc.ejecutar(
            rut="11111111-1",
            nombre="María López",
            correo="maria@test.com",
            telefono="+56911111111",
            id_sucursal=1,
            password="ClaveSegura123",
            meta_mensual_uf=100,
            codigo_roles=["EJECUTIVO"],
            porcentaje_comision=0.05,
        )

        assert resultado is True
        repositorio_mock.registrar.assert_called_once()

    def test_registrar_rut_duplicado(self, repositorio_mock, auth_service_mock):
        repositorio_mock.buscar.return_value = crear_usuario_mock()

        uc = RegistrarUsuarioUseCase(repositorio_mock, auth_service_mock)

        with pytest.raises(RecursoYaExisteException, match="El usuario ya existe"):
            uc.ejecutar(
                rut="12345678-9",
                nombre="Test",
                correo="test@test.com",
                telefono="+56912345678",
                id_sucursal=1,
                password="ClaveSegura123",
                meta_mensual_uf=None,
                codigo_roles=["EJECUTIVO"],
                porcentaje_comision=None,
            )

    def test_registrar_correo_duplicado(self, repositorio_mock, auth_service_mock):
        repositorio_mock.buscar.return_value = None
        repositorio_mock.existe_correo.return_value = True

        uc = RegistrarUsuarioUseCase(repositorio_mock, auth_service_mock)

        with pytest.raises(RecursoYaExisteException, match="El correo ya está en uso"):
            uc.ejecutar(
                rut="11111111-1",
                nombre="Test",
                correo="duplicado@test.com",
                telefono="+56911111111",
                id_sucursal=1,
                password="ClaveSegura123",
                meta_mensual_uf=None,
                codigo_roles=["EJECUTIVO"],
                porcentaje_comision=None,
            )

    def test_registrar_telefono_duplicado(self, repositorio_mock, auth_service_mock):
        repositorio_mock.buscar.return_value = None
        repositorio_mock.existe_correo.return_value = False
        repositorio_mock.existe_telefono.return_value = True

        uc = RegistrarUsuarioUseCase(repositorio_mock, auth_service_mock)

        with pytest.raises(RecursoYaExisteException, match="El teléfono ya está en uso"):
            uc.ejecutar(
                rut="11111111-1",
                nombre="Test",
                correo="test@test.com",
                telefono="+56999999999",
                id_sucursal=1,
                password="ClaveSegura123",
                meta_mensual_uf=None,
                codigo_roles=["EJECUTIVO"],
                porcentaje_comision=None,
            )

    def test_registrar_sin_roles(self, repositorio_mock, auth_service_mock):
        uc = RegistrarUsuarioUseCase(repositorio_mock, auth_service_mock)

        with pytest.raises(ConflictoEnAccionException, match="Debe asignar al menos un rol"):
            uc.ejecutar(
                rut="11111111-1",
                nombre="Test",
                correo="test@test.com",
                telefono="+56911111111",
                id_sucursal=1,
                password="ClaveSegura123",
                meta_mensual_uf=None,
                codigo_roles=[],
                porcentaje_comision=None,
            )

    def test_registrar_hashea_password(self, repositorio_mock, auth_service_mock):
        repositorio_mock.buscar.return_value = None
        repositorio_mock.existe_correo.return_value = False
        repositorio_mock.existe_telefono.return_value = False
        repositorio_mock.registrar.return_value = True

        uc = RegistrarUsuarioUseCase(repositorio_mock, auth_service_mock)
        uc.ejecutar(
            rut="11111111-1",
            nombre="Test",
            correo="test@test.com",
            telefono="+56911111111",
            id_sucursal=1,
            password="PasswordSecreta1",
            meta_mensual_uf=None,
            codigo_roles=["EJECUTIVO"],
            porcentaje_comision=None,
        )

        auth_service_mock.hash_password.assert_called_once_with("PasswordSecreta1")

    def test_registrar_password_debil_es_rechazada(self, repositorio_mock, auth_service_mock):
        repositorio_mock.buscar.return_value = None
        repositorio_mock.existe_correo.return_value = False
        repositorio_mock.existe_telefono.return_value = False

        uc = RegistrarUsuarioUseCase(repositorio_mock, auth_service_mock)

        with pytest.raises(DatoInvalidoException, match="al menos 12 caracteres"):
            uc.ejecutar(
                rut="11111111-1",
                nombre="Test",
                correo="test@test.com",
                telefono="+56911111111",
                id_sucursal=1,
                password="password123",
                meta_mensual_uf=None,
                codigo_roles=["EJECUTIVO"],
                porcentaje_comision=None,
            )

        auth_service_mock.hash_password.assert_not_called()


@pytest.mark.unit
class TestObtenerUsuarioUseCase:

    def test_obtener_usuario_exitoso(self, repositorio_mock):
        usuario = crear_usuario_mock(rut="12345678-9")
        repositorio_mock.buscar.return_value = usuario
        authorization_service_mock = MagicMock()
        authorization_service_mock.usuario_puede_ver_perfil.return_value = True

        uc = ObtenerUsuarioUseCase(repositorio_mock, authorization_service_mock)
        resultado = uc.ejecutar(rut_consultado="12345678-9", usuario_accion=crear_usuario_mock())

        assert resultado.rut == "12345678-9"

    def test_obtener_usuario_no_encontrado(self, repositorio_mock):
        repositorio_mock.buscar.return_value = None
        authorization_service_mock = MagicMock()
        authorization_service_mock.usuario_puede_ver_perfil.return_value = True

        uc = ObtenerUsuarioUseCase(repositorio_mock, authorization_service_mock)

        with pytest.raises(RecursoNoEncontradoException, match="Usuario no encontrado"):
            uc.ejecutar(rut_consultado="99999999-9", usuario_accion=crear_usuario_mock())

    def test_obtener_usuario_sin_permiso_retorna_403(self, repositorio_mock):
        authorization_service_mock = MagicMock()
        authorization_service_mock.usuario_puede_ver_perfil.return_value = False

        uc = ObtenerUsuarioUseCase(repositorio_mock, authorization_service_mock)

        with pytest.raises(UsuarioNoAutorizadoException):
            uc.ejecutar(rut_consultado="99999999-9", usuario_accion=crear_usuario_mock())

        repositorio_mock.buscar.assert_not_called()


@pytest.mark.unit
class TestObtenerUsuariosUseCase:

    def test_obtener_usuarios_lista(self, repositorio_mock):
        usuarios = [crear_usuario_mock(rut="11111111-1"), crear_usuario_mock(rut="22222222-2")]
        repositorio_mock.obtener_todos.return_value = usuarios

        uc = ObtenerUsuariosUseCase(repositorio_mock)
        resultado = uc.ejecutar()

        assert len(resultado) == 2

    def test_obtener_usuarios_lista_vacia(self, repositorio_mock):
        repositorio_mock.obtener_todos.return_value = []

        uc = ObtenerUsuariosUseCase(repositorio_mock)
        resultado = uc.ejecutar()

        assert len(resultado) == 0


@pytest.mark.unit
class TestEliminarUsuarioUseCase:

    def test_eliminar_exitoso(self, repositorio_mock):
        usuario = crear_usuario_mock(rut="12345678-9")
        repositorio_mock.buscar.return_value = usuario
        repositorio_mock.eliminar.return_value = True

        uc = EliminarUsuarioUseCase(repositorio_mock)
        uc.ejecutar("12345678-9")

        repositorio_mock.eliminar.assert_called_once_with("12345678-9")

    def test_eliminar_no_encontrado(self, repositorio_mock):
        repositorio_mock.buscar.return_value = None

        uc = EliminarUsuarioUseCase(repositorio_mock)

        with pytest.raises(RecursoNoEncontradoException, match="Usuario no encontrado"):
            uc.ejecutar("99999999-9")


@pytest.mark.unit
class TestActualizarUsuarioUseCase:

    def test_actualizar_exitoso(self, repositorio_mock, auth_service_mock):
        usuario_existente = crear_usuario_mock(rut="12345678-9")
        repositorio_mock.buscar.return_value = usuario_existente
        repositorio_mock.existe_correo.return_value = False
        repositorio_mock.existe_telefono.return_value = False
        repositorio_mock.actualizar.return_value = True
        repositorio_mock.asignar_roles.return_value = True

        uc = ActualizarUsuarioUseCase(repositorio_mock, auth_service_mock)
        resultado = uc.ejecutar(
            rut="12345678-9",
            nombre="Nombre Actualizado",
            correo="nuevo@test.com",
            telefono="+56999999999",
            id_sucursal=1,
            password=None,
            meta_mensual_uf=200,
            codigo_roles=["ADMIN"],
            porcentaje_comision=0.10,
            habilitado=True,
        )

        assert resultado is True
        repositorio_mock.actualizar.assert_called_once()
        repositorio_mock.asignar_roles.assert_called_once_with("12345678-9", ["ADMIN"])

    def test_actualizar_usuario_no_encontrado(self, repositorio_mock, auth_service_mock):
        repositorio_mock.buscar.return_value = None

        uc = ActualizarUsuarioUseCase(repositorio_mock, auth_service_mock)

        with pytest.raises(RecursoNoEncontradoException, match="El usuario no existe"):
            uc.ejecutar(
                rut="99999999-9",
                nombre="Test",
                correo="test@test.com",
                telefono="+56912345678",
                id_sucursal=1,
                password=None,
                meta_mensual_uf=None,
                codigo_roles=["ADMIN"],
                porcentaje_comision=None,
                habilitado=True,
            )

    def test_actualizar_correo_duplicado(self, repositorio_mock, auth_service_mock):
        usuario = crear_usuario_mock(rut="12345678-9", correo="original@test.com")
        repositorio_mock.buscar.return_value = usuario
        repositorio_mock.existe_correo.return_value = True

        uc = ActualizarUsuarioUseCase(repositorio_mock, auth_service_mock)

        with pytest.raises(RecursoYaExisteException, match="El correo ya está en uso"):
            uc.ejecutar(
                rut="12345678-9",
                nombre="Test",
                correo="duplicado@test.com",
                telefono="+56912345678",
                id_sucursal=1,
                password=None,
                meta_mensual_uf=None,
                codigo_roles=["ADMIN"],
                porcentaje_comision=None,
                habilitado=True,
            )

    def test_actualizar_con_password(self, repositorio_mock, auth_service_mock):
        usuario = crear_usuario_mock(rut="12345678-9")
        repositorio_mock.buscar.return_value = usuario
        repositorio_mock.existe_correo.return_value = False
        repositorio_mock.existe_telefono.return_value = False
        repositorio_mock.actualizar.return_value = True
        repositorio_mock.asignar_roles.return_value = True

        uc = ActualizarUsuarioUseCase(repositorio_mock, auth_service_mock)
        uc.ejecutar(
            rut="12345678-9",
            nombre="Test",
            correo="test@test.com",
            telefono="+56912345678",
            id_sucursal=1,
            password="NuevaPassword12",
            meta_mensual_uf=None,
            codigo_roles=["ADMIN"],
            porcentaje_comision=None,
            habilitado=True,
        )

        auth_service_mock.hash_password.assert_called_once_with("NuevaPassword12")

    def test_actualizar_con_password_revoca_sesiones_del_target(self, repositorio_mock, auth_service_mock):
        from uuid import uuid4

        usuario = crear_usuario_mock(rut="12345678-9")
        repositorio_mock.buscar.return_value = usuario
        repositorio_mock.existe_correo.return_value = False
        repositorio_mock.existe_telefono.return_value = False
        repositorio_mock.actualizar.return_value = True
        repositorio_mock.asignar_roles.return_value = True

        sesion_id_ejecutor = uuid4()
        uc = ActualizarUsuarioUseCase(repositorio_mock, auth_service_mock)
        uc.ejecutar(
            rut="12345678-9",
            nombre="Test",
            correo="test@test.com",
            telefono="+56912345678",
            id_sucursal=1,
            password="NuevaPassword12",
            meta_mensual_uf=None,
            codigo_roles=["ADMIN"],
            porcentaje_comision=None,
            habilitado=True,
            sesion_id_ejecutor=sesion_id_ejecutor,
        )

        auth_service_mock.revocar_todas_las_sesiones_excepto.assert_called_once_with(
            "12345678-9", sesion_id_ejecutor, motivo="password_change"
        )

    def test_actualizar_sin_password_no_revoca_sesiones(self, repositorio_mock, auth_service_mock):
        usuario = crear_usuario_mock(rut="12345678-9")
        repositorio_mock.buscar.return_value = usuario
        repositorio_mock.existe_correo.return_value = False
        repositorio_mock.existe_telefono.return_value = False
        repositorio_mock.actualizar.return_value = True
        repositorio_mock.asignar_roles.return_value = True

        uc = ActualizarUsuarioUseCase(repositorio_mock, auth_service_mock)
        uc.ejecutar(
            rut="12345678-9",
            nombre="Test",
            correo="test@test.com",
            telefono="+56912345678",
            id_sucursal=1,
            password=None,
            meta_mensual_uf=None,
            codigo_roles=["ADMIN"],
            porcentaje_comision=None,
            habilitado=True,
        )

        auth_service_mock.revocar_todas_las_sesiones_excepto.assert_not_called()

    def test_actualizar_con_password_debil_es_rechazada(self, repositorio_mock, auth_service_mock):
        usuario = crear_usuario_mock(rut="12345678-9")
        repositorio_mock.buscar.return_value = usuario
        repositorio_mock.existe_correo.return_value = False
        repositorio_mock.existe_telefono.return_value = False

        uc = ActualizarUsuarioUseCase(repositorio_mock, auth_service_mock)

        with pytest.raises(DatoInvalidoException):
            uc.ejecutar(
                rut="12345678-9",
                nombre="Test",
                correo="test@test.com",
                telefono="+56912345678",
                id_sucursal=1,
                password="nueva_password",
                meta_mensual_uf=None,
                codigo_roles=["ADMIN"],
                porcentaje_comision=None,
                habilitado=True,
            )

        auth_service_mock.hash_password.assert_not_called()

    def test_actualizar_sin_roles(self, repositorio_mock, auth_service_mock):
        usuario = crear_usuario_mock()
        repositorio_mock.buscar.return_value = usuario

        uc = ActualizarUsuarioUseCase(repositorio_mock, auth_service_mock)

        with pytest.raises(ConflictoEnAccionException, match="Debe asignar al menos un rol"):
            uc.ejecutar(
                rut="12345678-9",
                nombre="Test",
                correo="test@test.com",
                telefono="+56912345678",
                id_sucursal=1,
                password=None,
                meta_mensual_uf=None,
                codigo_roles=[],
                porcentaje_comision=None,
                habilitado=True,
            )
