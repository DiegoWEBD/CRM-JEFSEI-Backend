from datetime import datetime, timezone

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.cotizacion.cotizacion_factory import CotizacionFactory
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.cotizacion.repositorio_cotizaciones import RepositorioCotizaciones
from app.dominio.company_seguros.repositorio_company_seguros import RepositorioCompanySeguros
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_SLA
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion


class RegistrarCotizacionASolicitudUseCase:

    def __init__(
        self, 
        repositorio_companies: RepositorioCompanySeguros,
        repositorio_solicitudes_cotizacion: RepositorioSolicitudesCotizacion,
        repositorio_cotizaciones: RepositorioCotizaciones,
        authorization_service: AuthorizationService,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_notificaciones: RepositorioNotificaciones,
        servicio_alertas: ServicioAlertasProceso
    ) -> None:
        self.repositorio_cotizaciones = repositorio_cotizaciones
        self.authorization_service = authorization_service
        self.repositorio_solicitudes_cotizacion = repositorio_solicitudes_cotizacion
        self.repositorio_companies = repositorio_companies
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.repositorio_notificaciones = repositorio_notificaciones
        self.servicio_alertas = servicio_alertas

    def ejecutar(
        self, 
        rut_usuario: str,
        id_solicitud: int, 
        monto_total_asegurado: float,
        asistencia_afecta: float,
        asistencia_excenta: float,
        id_company: int,
        fecha_emision: str,
        fecha_vencimiento: str,
        tipo: str,
        tasa_afecta: float | None = None,
        tasa_excenta: float | None = None,
        tasa_politica: float | None = None,
        prima_afecta: float | None = None,
        prima_excenta: float | None = None,
        nombre_archivo: str | None = None
    ):
        if not self.repositorio_solicitudes_cotizacion.existe_solicitud(id_solicitud):
            raise RecursoNoEncontradoException('Solicitud no encontrada')
        
        if not self.authorization_service.usuario_puede_ver_solicitud_cotizacion(rut_usuario, id_solicitud):
            raise UsuarioNoAutorizadoException

        cotizacion = CotizacionFactory.crear(
            monto_total_asegurado=monto_total_asegurado,
            asistencia_afecta=asistencia_afecta,
            asistencia_excenta=asistencia_excenta,
            id_company=id_company,
            fecha_emision=datetime.fromisoformat(fecha_emision),
            fecha_vencimiento=datetime.fromisoformat(fecha_vencimiento),
            tipo=tipo,
            tasa_afecta=tasa_afecta,
            tasa_excenta=tasa_excenta,
            tasa_politica=tasa_politica,
            prima_afecta=prima_afecta,
            prima_excenta=prima_excenta,
            nombre_archivo=nombre_archivo,
        )
        
        if self.repositorio_companies.buscar(cotizacion.company.id) is None:
            raise RecursoNoEncontradoException('Compañía no encontrada')

        self.repositorio_cotizaciones.registrar_cotizacion_a_solicitud(
            id_solicitud, cotizacion, rut_usuario
        )

        # La cotización cambia el estado del proceso: la alerta de
        # permanencia en el estado anterior deja de ser relevante.
        proceso_comercial = self.repositorio_procesos_comerciales.buscar_por_solicitud_cotizacion(
            id_solicitud
        )

        if proceso_comercial is not None:
            ahora = datetime.now(tz=timezone.utc)
            destinatarios = self.servicio_alertas.marcar_leidas(
                proceso_comercial.id, TIPOS_ALERTA_SLA, ahora
            )

            if destinatarios:
                hub.publicar_desde_hilo(
                    destinatarios,
                    {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_leidas_cambio_estado'},
                )
