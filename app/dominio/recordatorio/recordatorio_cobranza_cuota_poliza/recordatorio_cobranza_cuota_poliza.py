from datetime import datetime

from app.dominio.recordatorio.recordatorio import Recordatorio


class RecordatorioCobranzaCuotaPoliza(Recordatorio):
    
    def __init__(
        self, 
        id: int,
        id_prospecto: int | None,
        nombre_prospecto: str | None,
        numero_poliza: str,
        titulo: str, 
        detalle: str | None, 
        completado: bool, 
        tipo_gestion: str, 
        prioridad: str, 
        fecha_recordatorio: datetime
    ):
        super().__init__(id, titulo, detalle, completado, tipo_gestion, prioridad, fecha_recordatorio)
        
        self.id_prospecto = id_prospecto
        self.nombre_prospecto = nombre_prospecto
        self.numero_poliza = numero_poliza