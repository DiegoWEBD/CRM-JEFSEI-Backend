from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial
from app.infraestructura.estudio_comercial_condominio.adaptadores.estudio_comercial_condominio_json_adapter import EstudioComercialCondominioJsonAdapter
from app.infraestructura.historial_estado.adaptadores.historial_estado_json_adapter import HistorialEstadoJsonAdapter
from app.infraestructura.solicitud_cotizacion.adaptadores.solicitud_cotizacion_json_adapter import SolicitudCotizacionJsonAdapter
from app.infraestructura.usuario.adaptadores.usuario_json_resumen_adapter import UsuarioJsonResumenAdapter
from app.presentacion.api.proceso_comercial.dto.proceso_comercial_json import ProcesoComercialJson


class ProcesoComercialJsonAdapter:
    def __init__(self, proceso_comercial: ProcesoComercial):      
        self.proceso_comercial = proceso_comercial

    def to_json(self) -> ProcesoComercialJson:
        if not self.proceso_comercial.id:
            raise Exception('Proceso Comercial inválido')
        
        return ProcesoComercialJson(
            id=self.proceso_comercial.id,
            historial_estados=[HistorialEstadoJsonAdapter(historial).to_historial_estado_json() for historial in self.proceso_comercial.historial_estados],
            ejecutivo_comercial=UsuarioJsonResumenAdapter(self.proceso_comercial.ejecutivo_comercial).to_usuario_json_resumen() if self.proceso_comercial.ejecutivo_comercial else None,
            ejecutivo_evaluacion=UsuarioJsonResumenAdapter(self.proceso_comercial.ejecutivo_evaluacion).to_usuario_json_resumen() if self.proceso_comercial.ejecutivo_evaluacion else None,
            solicitudes_cotizacion=[SolicitudCotizacionJsonAdapter(solicitud).to_json() for solicitud in self.proceso_comercial.solicitudes_cotizacion],
            estudio=EstudioComercialCondominioJsonAdapter(self.proceso_comercial.estudio).to_json() if self.proceso_comercial.estudio else None
        )