from app.dominio.estado_informativo_proceso_comercial.transicion_estado_proceso_comercial import TransicionEstadoProcesoComercial
from app.presentacion.api.estado.dto.transicion_admin_json import TransicionAdminJson


class TransicionAdminMapper:

    def __init__(self, transiciones: list[TransicionEstadoProcesoComercial]) -> None:
        self.transiciones = transiciones

    def map(self) -> list[TransicionAdminJson]:
        return [self.map_one(t) for t in self.transiciones]

    @staticmethod
    def map_one(t: TransicionEstadoProcesoComercial) -> TransicionAdminJson:
        return TransicionAdminJson(
            codigo_estado_origen=t.codigo_estado_origen,
            codigo_estado_destino=t.codigo_estado_destino,
            nombre_estado_origen=t.nombre_estado_origen,
            nombre_estado_destino=t.nombre_estado_destino,
            es_manual=t.es_manual,
            es_principal=t.es_principal,
            accion_requerida=t.accion_requerida,
            dias_limite=t.dias_limite,
        )
