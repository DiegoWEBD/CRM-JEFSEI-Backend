from app.aplicacion.prospecto.servicios.consulta_prospectos_service import ConsultaProspectosService
from app.aplicacion.prospecto.use_cases.asignar_ejecutivo_comercial import AsignarEjecutivoComercialUseCase
from app.aplicacion.prospecto.use_cases.obtener_prospecto import ObtenerProspectoUseCase
from app.aplicacion.prospecto.use_cases.registrar_prospecto import RegistrarProspectoUseCase
from app.infraestructura.prospecto.repositorio_prospectos_postgres import RepositorioProspectosPostgres
from app.infraestructura.prospecto.servicios.consulta_prospectos_postgres_service import ConsultaProspectosPostgresService
from app.infraestructura.usuario.repositorio_usuarios_postgres import RepositorioUsuariosPostgres


def get_consulta_prospectos_service() -> ConsultaProspectosService:
    return ConsultaProspectosPostgresService()

def get_obtener_prospecto_use_case():
    repositorio = RepositorioProspectosPostgres()
    return ObtenerProspectoUseCase(repositorio)

def get_registrar_prospecto_use_case():
    repositorio = RepositorioProspectosPostgres()
    return RegistrarProspectoUseCase(repositorio)

def get_asignar_ejecutivo_comercial_use_case():
    repositorio_prospectos = RepositorioProspectosPostgres()
    repositorio_usuarios = RepositorioUsuariosPostgres()
    return AsignarEjecutivoComercialUseCase(repositorio_prospectos, repositorio_usuarios)