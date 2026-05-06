from app.aplicacion.prospecto.servicios.consulta_prospectos_service import ConsultaProspectosService
from app.aplicacion.prospecto.use_cases.registrar_prospecto import RegistrarProspectoUseCase
from app.infraestructura.prospecto.repositorio_prospectos_postgres import RepositorioProspectosPostgres
from app.infraestructura.prospecto.servicios.consulta_prospectos_postgres_service import ConsultaProspectosPostgresService


def get_consulta_prospectos_service() -> ConsultaProspectosService:
    return ConsultaProspectosPostgresService()

def get_registrar_prospecto_use_case():
    repositorio = RepositorioProspectosPostgres()
    return RegistrarProspectoUseCase(repositorio)