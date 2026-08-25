from app.dominio.configuracion_condominio.repositorio_configuracion_condominio import RepositorioConfiguracionCondominio
from app.dominio.configuracion_condominio.valor_uf_region import ValorUfRegion


class ObtenerTodosValoresUfRegionUseCase:

    def __init__(self, repositorio: RepositorioConfiguracionCondominio):
        self.repositorio = repositorio

    def ejecutar(self) -> list[ValorUfRegion]:
        return self.repositorio.obtener_todos_valores_uf_region()
