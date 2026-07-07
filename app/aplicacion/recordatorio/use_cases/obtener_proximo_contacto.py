from app.dominio.recordatorio.recordatorio_usuario.recordatorio_usuario import RecordatorioUsuario
from app.dominio.recordatorio.repositorio_recordatorios import RepositorioRecordatorios


class ObtenerProximoContactoUseCase:

    def __init__(self, repositorio_recordatorio: RepositorioRecordatorios) -> None:
        self.repositorio_recordatorio = repositorio_recordatorio

    def ejecutar(self, rut_usuario: str, id_prospecto: int) -> RecordatorioUsuario | None:
        return self.repositorio_recordatorio.obtener_proximo_contacto(rut_usuario, id_prospecto)
