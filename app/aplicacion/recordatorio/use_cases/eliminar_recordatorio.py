from app.dominio.recordatorio.repositorio_recordatorios import RepositorioRecordatorios


class EliminarRecordatorioUseCase:

    def __init__(self, repositorio_recordatorios: RepositorioRecordatorios):
        self.repositorio_recordatorios = repositorio_recordatorios

    def ejecutar(self, id: int) -> None:
        self.repositorio_recordatorios.eliminar(id=id)
