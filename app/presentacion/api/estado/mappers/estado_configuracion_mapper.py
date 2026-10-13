from app.dominio.estado_informativo_proceso_comercial.estado_informativo_proceso_comercial import EstadoInformativoProcesoComercial
from app.presentacion.api.estado.dto.estado_configuracion_json import EstadoConfiguracionJson


class EstadoConfiguracionMapper:

    def __init__(self, estados: list[EstadoInformativoProcesoComercial]) -> None:
        self.estados = estados

    def map(self) -> list[EstadoConfiguracionJson]:
        return [self.map_one(estado) for estado in self.estados]

    @staticmethod
    def map_one(estado: EstadoInformativoProcesoComercial) -> EstadoConfiguracionJson:
        return EstadoConfiguracionJson(
            codigo=estado.codigo,
            nombre=estado.nombre,
            codigo_etapa=estado.etapa.codigo,
            nombre_etapa=estado.etapa.nombre,
            probabilidad_cierre=estado.probabilidad_cierre or 0.0,
            dias_limite=estado.dias_limite,
            rol_responsable=estado.rol_responsable,
            nombre_rol_responsable=estado.nombre_rol_responsable,
            cantidad_transiciones=estado.cantidad_transiciones,
        )
