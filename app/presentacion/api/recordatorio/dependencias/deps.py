from app.aplicacion.recordatorio.use_cases.obtener_recordatorios import ObtenerRecordatoriosUsuarioUseCase
from app.aplicacion.recordatorio.use_cases.registrar_recordatorio import RegistrarRecordatorioUseCase
from app.infraestructura.prospecto.repositorio_prospectos_postgres import RepositorioProspectosPostgres
from app.infraestructura.recordatorio.repositorio_recordatorios_postgres import RepositorioRecordatoriosPostgres


def get_obtener_recordatorios_usuario_use_case():
    repositorio = RepositorioRecordatoriosPostgres()
    return ObtenerRecordatoriosUsuarioUseCase(repositorio)


def get_registrar_recordatorio_use_case():
    repositorio_recordatorios = RepositorioRecordatoriosPostgres()
    repositorio_prospectos = RepositorioProspectosPostgres()
    return RegistrarRecordatorioUseCase(repositorio_recordatorios, repositorio_prospectos)