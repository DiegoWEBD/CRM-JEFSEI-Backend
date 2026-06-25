from app.aplicacion.recordatorio.use_cases.obtener_recordatorios import ObtenerRecordatoriosUsuarioUseCase
from app.infraestructura.recordatorio.repositorio_recordatorios_postgres import RepositorioRecordatoriosPostgres


def get_obtener_recordatorios_usuario_use_case():
    repositorio = RepositorioRecordatoriosPostgres()
    return ObtenerRecordatoriosUsuarioUseCase(repositorio)