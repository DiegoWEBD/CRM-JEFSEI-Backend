from psycopg.rows import DictRow

from app.dominio.recordatorio.recordatorio_cobranza_cuota_poliza.recordatorio_cobranza_cuota_poliza import RecordatorioCobranzaCuotaPoliza


class DictRowRecordatorioCobranzaAdapter:

    def __init__(self, row: DictRow) -> None:
        self.row = row

    def to_recordatorio(self) -> RecordatorioCobranzaCuotaPoliza:
        
        id = self.row['id']
        id_prospecto = self.row['id_prospecto']
        nombre_riesgo = self.row['nombre_riesgo']
        titulo = self.row['titulo']
        detalle = self.row['detalle']
        completado = self.row['completado']
        tipo_gestion = self.row['tipo_gestion']
        prioridad = self.row['prioridad']
        fecha_recordatorio = self.row['fecha_recordatorio']
        numero_poliza = self.row['numero_poliza']
        

        return RecordatorioCobranzaCuotaPoliza(
            id=id,
            id_prospecto=id_prospecto,
            nombre_prospecto=nombre_riesgo,
            numero_poliza=numero_poliza,
            titulo=titulo,
            detalle=detalle,
            completado=completado,
            tipo_gestion=tipo_gestion,
            prioridad=prioridad,
            fecha_recordatorio=fecha_recordatorio
        )