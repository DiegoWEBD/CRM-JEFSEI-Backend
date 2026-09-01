import pytest
from tests.factories.usuario_factory import crear_usuario_mock, crear_rol_mock, crear_permiso_mock


@pytest.mark.unit
class TestUsuarioEntity:

    def test_crear_usuario_con_datos_basicos(self):
        usuario = crear_usuario_mock(rut="11111111-1", nombre="María López")
        assert usuario.rut == "11111111-1"
        assert usuario.nombre == "María López"
        assert usuario.habilitado is True
        assert usuario.eliminado is False

    def test_usuario_habilitado_por_defecto(self):
        usuario = crear_usuario_mock()
        assert usuario.habilitado is True

    def test_usuario_deshabilitado(self):
        usuario = crear_usuario_mock(habilitado=False)
        assert usuario.habilitado is False

    def test_usuario_eliminado(self):
        usuario = crear_usuario_mock(eliminado=True)
        assert usuario.eliminado is True

    def test_usuario_tiene_roles(self):
        permisos = [
            crear_permiso_mock(codigo="VER_USUARIOS"),
            crear_permiso_mock(codigo="REGISTRAR_USUARIOS"),
        ]
        rol = crear_rol_mock(codigo="ADMIN", permisos=permisos)
        usuario = crear_usuario_mock(roles=[rol])

        assert len(usuario.roles) == 1
        assert usuario.roles[0].codigo == "ADMIN"
        assert len(usuario.roles[0].permisos) == 2

    def test_usuario_sin_roles(self):
        usuario = crear_usuario_mock(roles=[])
        assert len(usuario.roles) == 0

    def test_usuario_tiene_sucursal(self):
        usuario = crear_usuario_mock()
        assert usuario.sucursal is not None
        assert usuario.sucursal.id == 1

    def test_usuario_meta_mensual_uf(self):
        usuario = crear_usuario_mock(meta_mensual_uf=200)
        assert usuario.meta_mensual_uf == 200

    def test_usuario_porcentaje_comision(self):
        usuario = crear_usuario_mock(porcentaje_comision=0.10)
        assert usuario.porcentaje_comision == 0.10


@pytest.mark.unit
class TestRolEntity:

    def test_crear_rol(self):
        rol = crear_rol_mock(codigo="EJECUTIVO", nombre="Ejecutivo Comercial")
        assert rol.codigo == "EJECUTIVO"
        assert rol.nombre == "Ejecutivo Comercial"

    def test_rol_con_permisos(self):
        permisos = [
            crear_permiso_mock(codigo="VER_PROSPECTOS"),
            crear_permiso_mock(codigo="CREAR_PROSPECTOS"),
        ]
        rol = crear_rol_mock(permisos=permisos)
        assert len(rol.permisos) == 2

    def test_rol_sin_permisos(self):
        rol = crear_rol_mock(permisos=[])
        assert len(rol.permisos) == 0
