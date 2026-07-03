from app.aplicacion.sucursal.use_cases.obtener_sucursales import ObtenerSucursalesUseCase
from app.infraestructura.sucursal.repositorio_sucursales_postgres import RepositorioSucursalesPostgres


def get_obtener_sucursales_use_case():
    repositorio = RepositorioSucursalesPostgres()
    return ObtenerSucursalesUseCase(repositorio)