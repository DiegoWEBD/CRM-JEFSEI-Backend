from app.aplicacion.producto.use_cases.actualizar_producto import ActualizarProductoUseCase
from app.aplicacion.producto.use_cases.crear_producto import CrearProductoUseCase
from app.aplicacion.producto.use_cases.eliminar_producto import EliminarProductoUseCase
from app.aplicacion.producto.use_cases.obtener_producto import ObtenerProductoUseCase
from app.aplicacion.producto.use_cases.obtener_productos import ObtenerProductosUseCase
from app.infraestructura.producto.repositorio_producto_postgres import RepositorioProductoPostgres


def get_obtener_productos_use_case():
    repositorio = RepositorioProductoPostgres()
    return ObtenerProductosUseCase(repositorio)


def get_obtener_producto_use_case():
    repositorio = RepositorioProductoPostgres()
    return ObtenerProductoUseCase(repositorio)


def get_crear_producto_use_case():
    repositorio = RepositorioProductoPostgres()
    return CrearProductoUseCase(repositorio)


def get_actualizar_producto_use_case():
    repositorio = RepositorioProductoPostgres()
    return ActualizarProductoUseCase(repositorio)


def get_eliminar_producto_use_case():
    repositorio = RepositorioProductoPostgres()
    return EliminarProductoUseCase(repositorio)
