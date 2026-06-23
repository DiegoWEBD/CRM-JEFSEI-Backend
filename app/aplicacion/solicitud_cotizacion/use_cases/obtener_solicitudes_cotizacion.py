from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion
from app.dominio.solicitud_cotizacion.solicitud_cotizacion import SolicitudCotizacion
from app.dominio.usuario.usuario import Usuario


class ObtenerSolicitudesCotizacionUseCase:
    
    def __init__(
        self, 
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_solicitudes: RepositorioSolicitudesCotizacion
    ):
        self.repositorio_solicitudes = repositorio_solicitudes
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales

    def ejecutar(self, id_proceso_comercial: int, usuario: Usuario) -> list[SolicitudCotizacion]:
        if not self.repositorio_procesos_comerciales.buscar(id_proceso_comercial):
            raise RecursoNoEncontradoException('Oportunidad no encontrada')

        return self.repositorio_solicitudes.obtener_solicitudes(id_proceso_comercial)