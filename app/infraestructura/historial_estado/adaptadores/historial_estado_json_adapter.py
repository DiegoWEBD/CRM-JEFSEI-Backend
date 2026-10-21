from app.dominio.historial_estado.historial_estado import HistorialEstado
from app.infraestructura.estado_informativo_proceso_comercial.estado_informativo_json_adapter import EstadoInformativoJsonAdapter
from app.infraestructura.usuario.adaptadores.usuario_json_adapter import UsuarioJsonAdapter
from app.presentacion.api.historial_estado.dto.historial_estado_json import HistorialEstadoJson


class HistorialEstadoJsonAdapter:

    def __init__(self, historial: HistorialEstado) -> None:
        self.historial = historial

    def to_json(self) -> HistorialEstadoJson:
        return HistorialEstadoJson(
            estado=EstadoInformativoJsonAdapter(self.historial.estado).to_json(),
            fecha_registro=self.historial.fecha_registro.isoformat(),
            observacion=self.historial.observacion,
            registrado_por=UsuarioJsonAdapter.Adapt(self.historial.registrado_por),
            dias_transcurridos=self.historial.dias_transcurridos
        )
