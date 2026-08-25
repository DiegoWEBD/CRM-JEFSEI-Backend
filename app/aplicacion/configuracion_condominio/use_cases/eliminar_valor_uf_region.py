from app.dominio.configuracion_condominio.repositorio_configuracion_condominio import RepositorioConfiguracionCondominio


class EliminarValorUfRegionUseCase:

    def __init__(self, repositorio: RepositorioConfiguracionCondominio):
        self.repositorio = repositorio

    def ejecutar(self, id: int) -> None:
        self.repositorio.eliminar_valor_uf_region(id)
