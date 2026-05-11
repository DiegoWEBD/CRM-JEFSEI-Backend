from fastapi.params import Depends

from app.aplicacion.linea_negocio.use_cases.obtener_lineas_de_negocio import ObtenerLineasDeNegocioUseCase
from app.dominio.linea_negocio import repositorio_lineas_negocio
from app.infraestructura.linea_negocio.repositorio_lineas_negocio_postgres import RepositorioLineasNegocioPostgres


def get_obtener_lineas_negocio_use_case() -> ObtenerLineasDeNegocioUseCase:
    repositorio = RepositorioLineasNegocioPostgres()
    return ObtenerLineasDeNegocioUseCase(repositorio)