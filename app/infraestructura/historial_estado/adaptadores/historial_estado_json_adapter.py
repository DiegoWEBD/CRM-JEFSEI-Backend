from app.dominio.estados.estado_particular.estado_particular import EstadoParticular
from app.presentacion.api.historial_estado.dto.historial_estado_json import HistorialEstadoJson


class HistorialEstadoJsonAdapter:
    def __init__(self, estado_particular: EstadoParticular):
        self.estado_particular = estado_particular

    def to_historial_estado_json(self) -> HistorialEstadoJson:

        dias_limite = self.estado_particular.dias_limite_particular

        if dias_limite is None:
            dias_limite = self.estado_particular.estado_base.dias_limite

        return HistorialEstadoJson(
            estado=self.estado_particular.estado_base.nombre,
            color=self.estado_particular.estado_base.color,
            fecha_registro=self.estado_particular.fecha_resgistro,
            dias_limite=dias_limite,
            dias_transcurridos=self.estado_particular.dias_transcurridos,
            proxima_accion=self.estado_particular.estado_base.siguiente_estado.accion if self.estado_particular.estado_base.siguiente_estado else None
        )