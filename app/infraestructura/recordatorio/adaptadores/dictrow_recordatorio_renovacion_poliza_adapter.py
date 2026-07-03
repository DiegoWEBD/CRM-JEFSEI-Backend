from psycopg.rows import DictRow

from app.dominio.recordatorio.recordatorio_renovacion_poliza.recordatorio_renovacion_poliza import RecordatorioRenovacionPoliza
from app.dominio.recordatorio.recordatorio_usuario.recordatorio_usuario import RecordatorioUsuario


class DictRowRecordatorioRenovacionPolizaAdapter:

    def __init__(self, row: DictRow) -> None:
        self.row = row

    def to_recordatorio(self) -> RecordatorioRenovacionPoliza:
        
        id = self.row['id']
        numero_poliza = self.row['numero_poliza']
        titulo = self.row['titulo']
        detalle = self.row['detalle']
        completado = self.row['completado']
        tipo_gestion = self.row['tipo_gestion']
        prioridad = self.row['prioridad']
        fecha_recordatorio = self.row['fecha_recordatorio']
        

        return RecordatorioRenovacionPoliza(
            id=id,
            numero_poliza=numero_poliza,
            titulo=titulo,
            detalle=detalle,
            completado=completado,
            tipo_gestion=tipo_gestion,
            prioridad=prioridad,
            fecha_recordatorio=fecha_recordatorio
        )