from app.dominio.estado_informativo_proceso_comercial.transicion_estado_proceso_comercial import TransicionEstadoProcesoComercial
from app.presentacion.api.estado.dto.transicion_manual_json import TransicionManualJson


class TransicionManualMapper:

    def __init__(self, transiciones: list[TransicionEstadoProcesoComercial]) -> None:
        self.transiciones = transiciones

    def map(self) -> list[TransicionManualJson]:
        return [
            TransicionManualJson(
                codigo=t.codigo_estado_destino,
                nombre=t.nombre_estado_destino,
                accion_requerida=t.accion_requerida,
            )
            for t in self.transiciones
        ]