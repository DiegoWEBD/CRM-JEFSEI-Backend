from app.dominio.recordatorio.recordatorio import Recordatorio
from app.dominio.recordatorio.repositorio_recordatorios import RepositorioRecordatorios


class ObtenerRecordatoriosUseCase:

    def __init__(self, repositorio_recordatorio: RepositorioRecordatorios) -> None:
        self.repositorio_recordatorio = repositorio_recordatorio

    def ejecutar(self, rut_usuario: str, fecha: str, id_prospecto: int | None) -> list[Recordatorio]:
        return self.repositorio_recordatorio.obtener_recordatorios(rut_usuario, fecha, id_prospecto)