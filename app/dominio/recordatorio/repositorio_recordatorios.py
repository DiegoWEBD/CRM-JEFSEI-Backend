from abc import ABC, abstractmethod

from app.dominio.recordatorio.recordatorio_cobranza_cuota_poliza.recordatorio_cobranza_cuota_poliza import RecordatorioCobranzaCuotaPoliza
from app.dominio.recordatorio.recordatorio_renovacion_poliza.recordatorio_renovacion_poliza import RecordatorioRenovacionPoliza
from app.dominio.recordatorio.recordatorio_usuario.recordatorio_usuario import RecordatorioUsuario


class RepositorioRecordatorios(ABC):
    
    @abstractmethod
    def obtener_recordatorios_usuario(self, rut_usuario: str, fecha: str, id_prospecto: int | None) -> list[RecordatorioUsuario]:
        pass

    @abstractmethod
    def obtener_recordatorios_renovacion(self, rut_usuario: str, fecha: str, id_prospecto: int | None) -> list[RecordatorioRenovacionPoliza]:
        pass

    @abstractmethod
    def obtener_recordatorios_cobranza(self, rut_usuario: str, fecha: str, id_prospecto: int | None) -> list[RecordatorioCobranzaCuotaPoliza]:
        pass

    @abstractmethod
    def registrar(self, rut_usuario: str, titulo: str, detalle: str | None, prioridad: str, tipo_gestion: str, fecha_recordatorio: str, id_prospecto: int | None) -> None:
        pass

    @abstractmethod
    def actualizar(self, id: int, titulo: str, detalle: str | None, prioridad: str, tipo_gestion: str, fecha_recordatorio: str, id_prospecto: int | None = None) -> None:
        pass

    @abstractmethod
    def completar(self, id: int) -> None:
        pass

    @abstractmethod
    def eliminar(self, id: int) -> None:
        pass

    @abstractmethod
    def obtener_proximo_contacto(self, rut_usuario: str, id_prospecto: int) -> RecordatorioUsuario | None:
        pass