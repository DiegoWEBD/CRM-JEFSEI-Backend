from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial
from app.infraestructura.estado_informativo_proceso_comercial.estado_informativo_json_adapter import EstadoInformativoJsonAdapter
from app.infraestructura.etapa_proceso_comercial.adaptadores.etapa_proceso_comercial_json_adapter import EtapaProcesoComercialJsonAdapter
from app.infraestructura.usuario.adaptadores.usuario_json_resumen_adapter import UsuarioJsonResumenAdapter
from app.presentacion.api.proceso_comercial.dto.proceso_comercial_json import ProcesoComercialJson


class ProcesoComercialJsonAdapter:

    def __init__(self, proceso: ProcesoComercial) -> None:
        self.proceso = proceso

    def to_json(self) -> ProcesoComercialJson:
        return ProcesoComercialJson(
            id=self.proceso.id,
            ejecutivo_comercial=UsuarioJsonResumenAdapter(self.proceso.ejecutivo_comercial).to_usuario_json_resumen() if self.proceso.ejecutivo_comercial else None,
            ejecutivo_evaluacion=UsuarioJsonResumenAdapter(self.proceso.ejecutivo_evaluacion).to_usuario_json_resumen() if self.proceso.ejecutivo_evaluacion else None,
            id_prospecto=self.proceso.id_prospecto,
            producto=self.proceso.producto.nombre,
            estado_actual=EstadoInformativoJsonAdapter(self.proceso.estado_actual).to_json(),
            etapa_actual=EtapaProcesoComercialJsonAdapter(self.proceso.estado_actual.etapa).to_json(),
            nombre_cliente=self.proceso.nombre_cliente,
            cerrado=self.proceso.cerrado
        )