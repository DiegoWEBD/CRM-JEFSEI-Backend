from app.aplicacion.comuna.use_cases.obtener_comunas import ObtenerComunasUseCase
from app.infraestructura.comuna.repositorio_comunas_postgres import RepositorioComunasPostgres


def get_obtener_comunas_use_case():
    repositorio = RepositorioComunasPostgres()
    return ObtenerComunasUseCase(repositorio)