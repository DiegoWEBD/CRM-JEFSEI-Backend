from app.dominio.configuracion_condominio.parametros_depreciacion import ParametrosDepreciacion
from app.dominio.configuracion_condominio.repositorio_configuracion_condominio import RepositorioConfiguracionCondominio


class GuardarParametrosDepreciacionUseCase:

    def __init__(self, repositorio: RepositorioConfiguracionCondominio):
        self.repositorio = repositorio

    def ejecutar(
        self,
        id: int | None,
        antiguedad_sin_depreciacion: int,
        porcentaje_por_anio: float,
        antiguedad_maxima: int,
        porcentaje_maximo: float
    ) -> ParametrosDepreciacion:
        params = ParametrosDepreciacion(
            id=id,
            antiguedad_sin_depreciacion=antiguedad_sin_depreciacion,
            porcentaje_por_anio=porcentaje_por_anio,
            antiguedad_maxima=antiguedad_maxima,
            porcentaje_maximo=porcentaje_maximo
        )
        return self.repositorio.guardar_parametros_depreciacion(params)
