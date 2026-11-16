from app.aplicacion.metricas.dto.metricas_dashboard_dto import (
    ProyeccionPrimaEsperadaDto,
)
from app.aplicacion.proyeccion.servicios.servicio_proyecciones_comerciales import (
    ServicioProyeccionesComerciales,
)
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import (
    RepositorioProcesosComerciales,
)


class ObtenerProyeccionPrimaEsperadaUseCase:
    """Proyección de prima esperada por mes de cierre estimado.

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

    def ejecutar(self) -> list[ProyeccionPrimaEsperadaDto]:
        procesos = self.repositorio_procesos.obtener_procesos_comerciales(
            id_prospecto=None,
            abiertos=True,
        )

        proyeccion = self.servicio_proyecciones.proyeccion_prima_esperada_por_mes(
            procesos
        )

        return [
            ProyeccionPrimaEsperadaDto(
                mes=item['mes'],
                prima_esperada=item['prima_esperada'],
            )
            for item in proyeccion
        ]
