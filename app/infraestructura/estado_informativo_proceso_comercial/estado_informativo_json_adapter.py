from app.dominio.estado_informativo_proceso_comercial.estado_informativo_proceso_comercial import EstadoInformativoProcesoComercial
from app.infraestructura.etapa_proceso_comercial.adaptadores.etapa_proceso_comercial_json_adapter import EtapaProcesoComercialJsonAdapter
from app.presentacion.api.estado_informativo.dto.estado_informativo_json import EstadoInformativoJson


class EstadoInformativoJsonAdapter:

    def __init__(self, estado: EstadoInformativoProcesoComercial) -> None:
        self.estado = estado

    def to_json(self) -> EstadoInformativoJson:
        return EstadoInformativoJson(
            codigo=self.estado.codigo,
            nombre=self.estado.nombre,
            etapa=EtapaProcesoComercialJsonAdapter(self.estado.etapa).to_json()
        )