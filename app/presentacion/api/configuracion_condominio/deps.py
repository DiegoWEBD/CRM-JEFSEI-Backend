from app.aplicacion.configuracion_condominio.use_cases.eliminar_valor_uf_region import EliminarValorUfRegionUseCase
from app.aplicacion.configuracion_condominio.use_cases.guardar_parametros_depreciacion import GuardarParametrosDepreciacionUseCase
from app.aplicacion.configuracion_condominio.use_cases.guardar_valor_uf_region import GuardarValorUfRegionUseCase
from app.aplicacion.configuracion_condominio.use_cases.obtener_parametros_depreciacion import ObtenerParametrosDepreciacionUseCase
from app.aplicacion.configuracion_condominio.use_cases.obtener_todos_valores_uf_region import ObtenerTodosValoresUfRegionUseCase
from app.aplicacion.configuracion_condominio.use_cases.obtener_valor_uf_region import ObtenerValorUfRegionUseCase
from app.infraestructura.configuracion_condominio.repositorio_configuracion_condominio_postgres import RepositorioConfiguracionCondominioPostgres


def _get_repositorio() -> RepositorioConfiguracionCondominioPostgres:
    return RepositorioConfiguracionCondominioPostgres()


def get_obtener_valor_uf_region_use_case() -> ObtenerValorUfRegionUseCase:
    return ObtenerValorUfRegionUseCase(_get_repositorio())


def get_obtener_todos_valores_uf_region_use_case() -> ObtenerTodosValoresUfRegionUseCase:
    return ObtenerTodosValoresUfRegionUseCase(_get_repositorio())


def get_guardar_valor_uf_region_use_case() -> GuardarValorUfRegionUseCase:
    return GuardarValorUfRegionUseCase(_get_repositorio())


def get_eliminar_valor_uf_region_use_case() -> EliminarValorUfRegionUseCase:
    return EliminarValorUfRegionUseCase(_get_repositorio())


def get_obtener_parametros_depreciacion_use_case() -> ObtenerParametrosDepreciacionUseCase:
    return ObtenerParametrosDepreciacionUseCase(_get_repositorio())


def get_guardar_parametros_depreciacion_use_case() -> GuardarParametrosDepreciacionUseCase:
    return GuardarParametrosDepreciacionUseCase(_get_repositorio())
