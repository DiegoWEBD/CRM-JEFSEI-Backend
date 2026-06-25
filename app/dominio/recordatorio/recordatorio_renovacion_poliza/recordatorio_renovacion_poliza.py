from datetime import datetime

from app.dominio.recordatorio.recordatorio import Recordatorio


class RecordatorioRenovacionPoliza(Recordatorio):
    
    def __init__(
        self, 
        id: int,
        numero_poliza: str,
        titulo: str, 
        detalle: str | None, 
        completado: bool, 
        tipo_gestion: str, 
        prioridad: str, 
        fecha_recordatorio: datetime
    ):
        super().__init__(id, titulo, detalle, completado, tipo_gestion, prioridad, fecha_recordatorio)
        
        self.numero_poliza = numero_poliza