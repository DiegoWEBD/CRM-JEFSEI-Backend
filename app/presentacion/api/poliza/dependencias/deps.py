from app.aplicacion.poliza.use_cases.obtener_polizas import ObtenerPolizasUseCase
from app.infraestructura.poliza.repositorio_polizas_postgres import RepositorioPolizasPostgres


def get_obtener_polizas_use_case():
    repositorio_polizas = RepositorioPolizasPostgres()
    return ObtenerPolizasUseCase(repositorio_polizas)