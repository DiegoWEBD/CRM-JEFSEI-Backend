from datetime import datetime

from app.dominio.recordatorio.recordatorio import Recordatorio


class RecordatorioUsuario(Recordatorio):
    
    def __init__(
        self, 
        id: int, 
        id_prospecto: int | None,
        nombre_prospecto: str | None,
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