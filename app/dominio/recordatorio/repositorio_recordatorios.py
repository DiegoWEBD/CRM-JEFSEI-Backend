from abc import ABC, abstractmethod

from app.dominio.recordatorio.recordatorio import Recordatorio


class RepositorioRecordatorios(ABC):
    
    @abstractmethod
    def obtener_recordatorios(self, rut_usuario: str, fecha: str, id_prospecto: int | None) -> list[Recordatorio]:
        pass

