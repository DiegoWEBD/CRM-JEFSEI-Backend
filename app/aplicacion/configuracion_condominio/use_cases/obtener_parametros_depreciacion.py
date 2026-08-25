from app.dominio.configuracion_condominio.parametros_depreciacion import ParametrosDepreciacion
from app.dominio.configuracion_condominio.repositorio_configuracion_condominio import RepositorioConfiguracionCondominio


class ObtenerParametrosDepreciacionUseCase:

    def __init__(self, repositorio: RepositorioConfiguracionCondominio):
        self.repositorio = repositorio

    def ejecutar(self) -> ParametrosDepreciacion | None:
        return self.repositorio.obtener_parametros_depreciacion()
