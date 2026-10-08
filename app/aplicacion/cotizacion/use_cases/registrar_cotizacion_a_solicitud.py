from datetime import datetime, timezone

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.cotizacion.repositorio_cotizaciones import RepositorioCotizaciones
from app.dominio.company_seguros.repositorio_company_seguros import RepositorioCompanySeguros
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_SLA
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion


class RegistrarCotizacionASolicitudUseCase:

    def __init__(
        self, 
        repositorio_companies: RepositorioCompanySeguros,
        repositorio_solicitudes_cotizacion: RepositorioSolicitudesCotizacion,
        repositorio_cotizaciones: RepositorioCotizaciones,
        authorization_service: AuthorizationService,
        repositorio_notificaciones: RepositorioNotificaciones,
        servicio_alertas: ServicioAlertasProceso
    ) -> None:
        self.repositorio_cotizaciones = repositorio_cotizaciones
        self.authorization_service = authorization_service
        self.repositorio_solicitudes_cotizacion = repositorio_solicitudes_cotizacion
        self.repositorio_companies = repositorio_companies
        self.repositorio_notificaciones = repositorio_notificaciones
        self.servicio_alertas = servicio_alertas

    def ejecutar(
        self, 
        rut_usuario: str,
        id_solicitud: int, 
        cotizacion: Cotizacion,
    ):
        if not self.repositorio_solicitudes_cotizacion.existe_solicitud(id_solicitud):
            raise RecursoNoEncontradoException('Solicitud no encontrada')
        
        if not self.authorization_service.usuario_puede_ver_solicitud_cotizacion(rut_usuario, id_solicitud):
            raise UsuarioNoAutorizadoException
        
        if self.repositorio_companies.buscar(cotizacion.company.id) is None:
            raise RecursoNoEncontradoException('Compañía no encontrada')

        id_proceso_comercial = self.repositorio_cotizaciones.registrar_cotizacion_a_solicitud(
            id_solicitud, cotizacion, rut_usuario
        )

        if id_proceso_comercial is not None:
            # La cotización cambia el estado del proceso: la alerta de
            # permanencia en el estado anterior deja de ser relevante.
            ahora = datetime.now(tz=timezone.utc)
            destinatarios = self.servicio_alertas.marcar_leidas(
                id_proceso_comercial, TIPOS_ALERTA_SLA, ahora
            )

            if destinatarios:
                hub.publicar_desde_hilo(
                    destinatarios,
                    {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_leidas_cambio_estado'},
                )
