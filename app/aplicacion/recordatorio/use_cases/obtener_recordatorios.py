from app.dominio.recordatorio.recordatorio import Recordatorio
from app.dominio.recordatorio.repositorio_recordatorios import RepositorioRecordatorios


class ObtenerRecordatoriosUsuarioUseCase:

    def __init__(self, repositorio_recordatorio: RepositorioRecordatorios) -> None:
        self.repositorio_recordatorio = repositorio_recordatorio

    def ejecutar(self, rut_usuario: str, fecha: str, id_prospecto: int | None) -> list[Recordatorio]:
        recordatorios: list[Recordatorio] = []
        recordatorios_usuario = self.repositorio_recordatorio.obtener_recordatorios_usuario(rut_usuario, fecha, id_prospecto)
        recordatorios_renovacion = self.repositorio_recordatorio.obtener_recordatorios_renovacion(rut_usuario, fecha, id_prospecto)
        
        for recordatorio in recordatorios_usuario:
            recordatorios.append(recordatorio)

        for recordatorio in recordatorios_renovacion:
            recordatorios.append(recordatorio)
        
        return recordatorios