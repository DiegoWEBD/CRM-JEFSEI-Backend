from app.aplicacion.recordatorio.use_cases.obtener_recordatorios import ObtenerRecordatoriosUseCase
from app.infraestructura.recordatorio.repositorio_recordatorios_postgres import RepositorioRecordatoriosPostgres


def get_obtener_recordatorios_use_case():
    repositorio = RepositorioRecordatoriosPostgres()
    return ObtenerRecordatoriosUseCase(repositorio)