from app.dominio.etapa_proceso_comercial.etapa_proceso_comercial import EtapaProcesoComercial
from app.presentacion.api.etapa_proceso_comercial.dto.etapa_proceso_comercial_json import EtapaProcesoComercialJson


class EtapaProcesoComercialJsonAdapter:

    def __init__(self, etapa: EtapaProcesoComercial) -> None:
        self.etapa = etapa

    def to_json(self) -> EtapaProcesoComercialJson:
        return EtapaProcesoComercialJson(
            codigo=self.etapa.codigo,
            nombre=self.etapa.nombre,
            dias_limite=self.etapa.dias_limite
        )