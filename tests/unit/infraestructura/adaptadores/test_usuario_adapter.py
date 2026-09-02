import pytest
from datetime import datetime, timezone
from app.infraestructura.usuario.adaptadores.tuplerows_usuario_adapter import TupleRowsUsuarioAdapter
from app.infraestructura.usuario.adaptadores.usuario_json_adapter import UsuarioJsonAdapter
from tests.factories.usuario_factory import crear_usuario_mock


@pytest.mark.unit
class TestTupleRowsUsuarioAdapter:

    def _make_row(
        self,
        rut="12345678-9",
        nombre="Juan Pérez",
        correo="juan@test.com",
        telefono="+56912345678",
        id_sucursal=1,
        nombre_sucursal="Sucursal Principal",
        codigo_rol="ADMIN",
        rol="Administrador",
        codigo_permiso="VER_USUARIOS",
        descripcion_permiso="Ver usuarios",
        password_hash="hash_123",
        meta_mensual_uf=100,
        fecha_registro=None,
        habilitado=True,
        eliminado=False,
        porcentaje_comision=0.05,
    ) -> dict:
        if fecha_registro is None:
            fecha_registro = datetime.now(tz=timezone.utc)
        return {
            "rut": rut,
            "nombre": nombre,
            "correo": correo,
            "telefono": telefono,
            "id_sucursal": id_sucursal,
            "nombre_sucursal": nombre_sucursal,
            "codigo_rol": codigo_rol,
            "rol": rol,
            "codigo_permiso": codigo_permiso,
            "descripcion_permiso": descripcion_permiso,
            "password_hash": password_hash,
            "meta_mensual_uf": meta_mensual_uf,
            "fecha_registro": fecha_registro,
            "habilitado": habilitado,
            "eliminado": eliminado,
            "porcentaje_comision": porcentaje_comision,
        }

    def test_adapter_con_una_fila(self):
        rows = [self._make_row()]
        adapter = TupleRowsUsuarioAdapter(rows)
        usuario = adapter.to_usuario()

        assert usuario.rut == "12345678-9"
        assert usuario.nombre == "Juan Pérez"
        assert usuario.correo == "juan@test.com"
        assert usuario.telefono == "+56912345678"
        assert usuario.sucursal.id == 1
        assert usuario.sucursal.nombre == "Sucursal Principal"
        assert len(usuario.roles) == 1
        assert usuario.roles[0].codigo == "ADMIN"
        assert len(usuario.roles[0].permisos) == 1

    def test_adapter_multiples_roles(self):
        rows = [
            self._make_row(codigo_rol="ADMIN", rol="Administrador", codigo_permiso="VER_USUARIOS", descripcion_permiso="Ver usuarios"),
            self._make_row(codigo_rol="ADMIN", rol="Administrador", codigo_permiso="CREAR_USUARIOS", descripcion_permiso="Crear usuarios"),
            self._make_row(codigo_rol="EJECUTIVO", rol="Ejecutivo", codigo_permiso="VER_PROSPECTOS", descripcion_permiso="Ver prospectos"),
        ]
        adapter = TupleRowsUsuarioAdapter(rows)
        usuario = adapter.to_usuario()

        assert len(usuario.roles) == 2
        admin = next(r for r in usuario.roles if r.codigo == "ADMIN")
        assert len(admin.permisos) == 2
        ejecutivo = next(r for r in usuario.roles if r.codigo == "EJECUTIVO")
        assert len(ejecutivo.permisos) == 1

    def test_adapter_rows_vacias_raises(self):
        with pytest.raises(ValueError, match="Usuario inválido"):
            TupleRowsUsuarioAdapter([])

    def test_adapter_fila_con_permiso_none(self):
        rows = [self._make_row(codigo_permiso=None, descripcion_permiso=None)]
        adapter = TupleRowsUsuarioAdapter(rows)
        usuario = adapter.to_usuario()

        assert len(usuario.roles) == 1
        assert len(usuario.roles[0].permisos) == 0


@pytest.mark.unit
class TestUsuarioJsonAdapter:

    def test_adapt_usuario_a_json(self):
        usuario = crear_usuario_mock(
            rut="12345678-9",
            nombre="Juan Pérez",
            correo="juan@test.com",
            telefono="+56912345678",
            meta_mensual_uf=100,
            porcentaje_comision=0.05,
        )

        json_data = UsuarioJsonAdapter.Adapt(usuario)

        assert json_data.rut == "12345678-9"
        assert json_data.nombre == "Juan Pérez"
        assert json_data.correo == "juan@test.com"
        assert json_data.telefono == "+56912345678"
        assert json_data.sucursal == "Sucursal Principal"
        assert json_data.meta_mensual_uf == 100
        assert json_data.porcentaje_comision == 0.05
        assert json_data.habilitado is True
        assert json_data.eliminado is False
        assert len(json_data.roles) == 1

    def test_adapt_usuario_sin_sucursal(self):
        usuario = crear_usuario_mock(sucursal=None)
        usuario.sucursal = None

        json_data = UsuarioJsonAdapter.Adapt(usuario)

        assert json_data.sucursal == ""

    def test_adapt_usuario_roles_son_dicts(self):
        usuario = crear_usuario_mock()
        json_data = UsuarioJsonAdapter.Adapt(usuario)

        for rol in json_data.roles:
            assert hasattr(rol, "codigo")
            assert hasattr(rol, "nombre")
