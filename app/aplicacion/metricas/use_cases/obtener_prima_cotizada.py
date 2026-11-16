from app.aplicacion.metricas.dto.metricas_dashboard_dto import PrimaCotizadaDto
from app.aplicacion.proyeccion.servicios.servicio_proyecciones_comerciales import (
    ServicioProyeccionesComerciales,
)
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import (
    RepositorioProcesosComerciales,
)


class ObtenerPrimaCotizadaUseCase:
    """Prima cotizada de las oportunidades abiertas.

    El cálculo lo hace `ServicioProyeccionesComerciales` (cotizaciones
    vigentes), el mismo que alimenta la vista de oportunidades.
    """

    def __init__(
        self,
        repositorio_procesos: RepositorioProcesosComerciales,
        servicio_proyecciones: ServicioProyeccionesComerciales,
    ):
        self.repositorio_procesos = repositorio_procesos
        self.servicio_proyecciones = servicio_proyecciones

    def ejecutar(self) -> PrimaCotizadaDto:
        procesos = self.repositorio_procesos.obtener_procesos_comerciales(
            id_prospecto=None,
            abiertos=True,
        )

        return PrimaCotizadaDto(
            prima_cotizada=self.servicio_proyecciones.prima_cotizada_total(procesos)
        )
