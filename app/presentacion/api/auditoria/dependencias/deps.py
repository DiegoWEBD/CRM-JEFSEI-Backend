from app.aplicacion.auditoria.servicio_auditoria import ServicioAuditoria
from app.aplicacion.auditoria.use_cases.obtener_registros_auditoria import ObtenerRegistrosAuditoriaUseCase
from app.infraestructura.auditoria.repositorio_auditoria_postgres import RepositorioAuditoriaPostgres


def get_servicio_auditoria() -> ServicioAuditoria:
    return ServicioAuditoria(RepositorioAuditoriaPostgres())


def get_obtener_registros_auditoria_use_case() -> ObtenerRegistrosAuditoriaUseCase:
    return ObtenerRegistrosAuditoriaUseCase(RepositorioAuditoriaPostgres())
