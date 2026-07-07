from app.aplicacion.recordatorio.use_cases.actualizar_recordatorio import ActualizarRecordatorioUseCase
from app.aplicacion.recordatorio.use_cases.completar_recordatorio import CompletarRecordatorioUseCase
from app.aplicacion.recordatorio.use_cases.eliminar_recordatorio import EliminarRecordatorioUseCase
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


def get_actualizar_recordatorio_use_case():
    repositorio_recordatorios = RepositorioRecordatoriosPostgres()
    return ActualizarRecordatorioUseCase(repositorio_recordatorios)


def get_completar_recordatorio_use_case():
    repositorio_recordatorios = RepositorioRecordatoriosPostgres()
    return CompletarRecordatorioUseCase(repositorio_recordatorios)


def get_eliminar_recordatorio_use_case():
    repositorio_recordatorios = RepositorioRecordatoriosPostgres()
    return EliminarRecordatorioUseCase(repositorio_recordatorios)