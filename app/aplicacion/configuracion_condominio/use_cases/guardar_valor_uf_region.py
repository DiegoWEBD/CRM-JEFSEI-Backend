from app.dominio.configuracion_condominio.repositorio_configuracion_condominio import RepositorioConfiguracionCondominio
from app.dominio.configuracion_condominio.valor_uf_region import ValorUfRegion


class GuardarValorUfRegionUseCase:

    def __init__(self, repositorio: RepositorioConfiguracionCondominio):
        self.repositorio = repositorio

    def ejecutar(self, id: int | None, region: str, valor_uf_m2: float) -> ValorUfRegion:
        valor = ValorUfRegion(
            id=id,
            region=region,
            valor_uf_m2=valor_uf_m2
        )
        return self.repositorio.guardar_valor_uf_region(valor)
