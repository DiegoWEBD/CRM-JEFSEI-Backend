from app.dominio.historial_estado.historial_estado import HistorialEstado
from app.presentacion.api.historial_estado.dto.historial_estado_json import HistorialEstadoJson


class HistorialEstadoJsonAdapter:
    def __init__(self, historial_estado: HistorialEstado):
        self.historial_estado = historial_estado

    def to_historial_estado_json(self) -> HistorialEstadoJson:

        dias_limite = self.historial_estado.estado_actual.dias_limite_particular

        if dias_limite is None:
            dias_limite = self.historial_estado.estado_actual.estado_base.dias_limite

        return HistorialEstadoJson(
            estado_anterior=self.historial_estado.estado_anterior.estado_base.codigo if self.historial_estado.estado_anterior else None,
            estado_actual=self.historial_estado.estado_actual.estado_base.codigo,
            fecha_registro=self.historial_estado.fecha_registro,
            dias_limite=dias_limite,
            dias_transcurridos=self.historial_estado.dias_transcurridos,
            proxima_accion=self.historial_estado.estado_actual.estado_base.siguiente_estado.accion if self.historial_estado.estado_actual.estado_base.siguiente_estado else None,
            motivo_cambio=self.historial_estado.motivo_cambio,
            cambiado_por=self.historial_estado.cambiado_por.nombre
        )