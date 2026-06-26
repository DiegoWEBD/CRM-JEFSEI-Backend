from app.dominio.sucursal.repositorio_sucursales import RepositorioSucursales
from app.dominio.sucursal.sucursal import Sucursal


class ObtenerSucursalesUseCase:

    def __init__(self, repositorio_sucursales: RepositorioSucursales) -> None:
        self.repositorio_sucursales = repositorio_sucursales

    def ejecutar(self) -> list[Sucursal]:
        return self.repositorio_sucursales.obtener_sucursales()