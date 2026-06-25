from psycopg.rows import DictRow

from app.dominio.recordatorio.recordatorio_usuario.recordatorio_usuario import RecordatorioUsuario


class DictRowRecordatorioUsuarioAdapter:

    def __init__(self, row: DictRow) -> None:
        self.row = row

    def to_recordatorio(self) -> RecordatorioUsuario:
        
        id = self.row['id']
        id_prospecto = self.row['id_prospecto']
        nombre_riesgo = self.row['nombre_riesgo']
        titulo = self.row['titulo']
        detalle = self.row['detalle']
        completado = self.row['completado']
        tipo_gestion = self.row['tipo_gestion']
        prioridad = self.row['prioridad']
        fecha_recordatorio = self.row['fecha_recordatorio']
        

        return RecordatorioUsuario(
            id=id,
            id_prospecto=id_prospecto,
            nombre_prospecto=nombre_riesgo,
            titulo=titulo,
            detalle=detalle,
            completado=completado,
            tipo_gestion=tipo_gestion,
            prioridad=prioridad,
            fecha_recordatorio=fecha_recordatorio
        )