from abc import ABC, abstractmethod

from app.dominio.configuracion_condominio.parametros_depreciacion import ParametrosDepreciacion
from app.dominio.configuracion_condominio.valor_uf_region import ValorUfRegion


class RepositorioConfiguracionCondominio(ABC):

    @abstractmethod
    def obtener_valor_uf_por_region(self, region: str) -> float | None: ...

    @abstractmethod
    def obtener_todos_valores_uf_region(self) -> list[ValorUfRegion]: ...

    @abstractmethod
    def guardar_valor_uf_region(self, valor: ValorUfRegion) -> ValorUfRegion: ...

    @abstractmethod
    def eliminar_valor_uf_region(self, id: int) -> None: ...

    @abstractmethod
    def obtener_parametros_depreciacion(self) -> ParametrosDepreciacion | None: ...

    @abstractmethod
    def guardar_parametros_depreciacion(self, params: ParametrosDepreciacion) -> ParametrosDepreciacion: ...
