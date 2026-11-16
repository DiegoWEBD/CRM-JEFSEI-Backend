from app.aplicacion.metricas.dto.metricas_dashboard_dto import (
    PrimaPotencialEstimadaDto,
)
from app.aplicacion.proyeccion.servicios.servicio_proyecciones_comerciales import (
    ServicioProyeccionesComerciales,
)
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import (
    RepositorioProcesosComerciales,
)


class ObtenerPrimaPotencialEstimadaUseCase:
    """Prima potencial estimada de las oportunidades abiertas.

    El cálculo lo hace `ServicioProyeccionesComerciales`, el mismo que
    alimenta la vista de oportunidades.
    """

    def __init__(
        self,
        repositorio_procesos: RepositorioProcesosComerciales,
        servicio_proyecciones: ServicioProyeccionesComerciales,
    ):
        self.repositorio_procesos = repositorio_procesos
        self.servicio_proyecciones = servicio_proyecciones

    def ejecutar(self) -> PrimaPotencialEstimadaDto:
        procesos = self.repositorio_procesos.obtener_procesos_comerciales(
            id_prospecto=None,
            abiertos=True,
        )

        return PrimaPotencialEstimadaDto(
            prima_potencial_estimada=self.servicio_proyecciones.prima_potencial_estimada_total(
                procesos
            )
        )
