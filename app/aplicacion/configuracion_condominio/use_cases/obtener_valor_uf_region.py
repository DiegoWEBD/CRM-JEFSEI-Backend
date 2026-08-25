from app.dominio.configuracion_condominio.repositorio_configuracion_condominio import RepositorioConfiguracionCondominio
from app.dominio.configuracion_condominio.valor_uf_region import ValorUfRegion


class ObtenerValorUfRegionUseCase:

    def __init__(self, repositorio: RepositorioConfiguracionCondominio):
        self.repositorio = repositorio

    def ejecutar(self, region: str) -> float | None:
        return self.repositorio.obtener_valor_uf_por_region(region)
