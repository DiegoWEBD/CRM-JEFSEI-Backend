from app.dominio.estudio_comercial.estudio_comercial_condominio.estudio_comercial_condominio import EstudioComercialCondominio
from app.dominio.historial_estado.historial_estado import HistorialEstado
from app.dominio.plan_pago.plan_pago import PlanPago
from app.dominio.poliza.poliza import Poliza
from app.dominio.solicitud_cotizacion.solicitud_cotizacion import SolicitudCotizacion
from app.dominio.usuario.usuario import Usuario

class ProcesoComercial:
    def __init__(
        self, 
        historial_estados: list[HistorialEstado], 
        ejecutivo_comercial: Usuario | None,
        ejecutivo_evaluacion: Usuario | None,
        solicitudes_cotizacion: list[SolicitudCotizacion],
        estudio: EstudioComercialCondominio | None,
        poliza: Poliza | None, 
        plan_pago: PlanPago | None,
        id: int | None = None
    ):
        self.id = id
        self.poliza = poliza
        self.plan_pago = plan_pago
        self.estudio = estudio
        self.ejecutivo_comercial = ejecutivo_comercial
        self.ejecutivo_evaluacion = ejecutivo_evaluacion
        self.historial_estados = historial_estados
        self.solicitudes_cotizacion = solicitudes_cotizacion