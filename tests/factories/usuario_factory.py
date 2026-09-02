from app.dominio.usuario.usuario import Usuario
from app.dominio.rol.rol import Rol
from app.dominio.permiso.permiso import Permiso
from app.dominio.sucursal.sucursal import Sucursal


def crear_permiso_mock(
    codigo: str = "VER_USUARIOS",
    descripcion: str = "Ver usuarios",
) -> Permiso:
    return Permiso(codigo=codigo, descripcion=descripcion)


def crear_rol_mock(
    codigo: str = "GERENTE",
    nombre: str = "Gerente",
    permisos: list[Permiso] | None = None,
) -> Rol:
    if permisos is None:
        permisos = [crear_permiso_mock()]
    return Rol(codigo=codigo, nombre=nombre, permisos=permisos)


def crear_sucursal_mock(
    id: int = 1,
    nombre: str = "Sucursal Principal",
) -> Sucursal:
    return Sucursal(id=id, nombre=nombre)


def crear_usuario_mock(
    rut: str = "12345678-9",
    nombre: str = "Juan Pérez",
    correo: str = "juan@test.com",
    telefono: str = "+56912345678",
    sucursal: Sucursal | None = None,
    habilitado: bool = True,
    eliminado: bool = False,
    meta_mensual_uf: int | None = 100,
    roles: list[Rol] | None = None,
    password_hash: str = "$2b$12$LJ3m4ys1Lz0Qf5T8VqYqyOJXHq5T8VqYqyOJXHq5T8VqYqyOJXHq",
    porcentaje_comision: float | None = 0.05,
) -> Usuario:
    if sucursal is None:
        sucursal = crear_sucursal_mock()
    if roles is None:
        roles = [crear_rol_mock()]
    return Usuario(
        rut=rut,
        nombre=nombre,
        correo=correo,
        telefono=telefono,
        sucursal=sucursal,
        habilitado=habilitado,
        eliminado=eliminado,
        meta_mensual_uf=meta_mensual_uf,
        roles=roles,
        password_hash=password_hash,
        porcentaje_comision=porcentaje_comision,
    )


def crear_usuario_admin_mock(**kwargs) -> Usuario:
    kwargs.setdefault("nombre", "Admin Test")
    kwargs.setdefault("correo", "admin@test.com")
    permisos_admin = [
        crear_permiso_mock(codigo="VER_USUARIOS", descripcion="Ver usuarios"),
        crear_permiso_mock(codigo="OBTENER_USUARIOS", descripcion="Obtener usuarios"),
        crear_permiso_mock(codigo="REGISTRAR_USUARIOS", descripcion="Registrar usuarios"),
        crear_permiso_mock(codigo="ADMINISTRAR_USUARIOS", descripcion="Administrar usuarios"),
        crear_permiso_mock(codigo="VER_METRICAS_GERENCIA", descripcion="Ver métricas gerencia"),
        crear_permiso_mock(codigo="VER_METRICAS_EJECUTIVO", descripcion="Ver métricas ejecutivo"),
    ]
    kwargs.setdefault("roles", [crear_rol_mock(codigo="ADMIN", nombre="Administrador", permisos=permisos_admin)])
    return crear_usuario_mock(**kwargs)
