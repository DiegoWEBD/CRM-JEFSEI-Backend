from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.authorization.authorization_service_factory import AuthorizationServiceFactory
from app.aplicacion.cotizacion.use_cases.registrar_renovacion_cotizada import RegistrarRenovacionCotizadaUseCase
from app.aplicacion.poliza.use_cases.actualizar_poliza import ActualizarPolizaUseCase
from app.aplicacion.poliza.use_cases.cancelar_poliza import CancelarPolizaUseCase
from app.aplicacion.poliza.use_cases.iniciar_renovacion_poliza import IniciarRenovacionPolizaUseCase
from app.aplicacion.poliza.use_cases.obtener_poliza import ObtenerPolizaUseCase
from app.aplicacion.poliza.use_cases.obtener_polizas import ObtenerPolizasUseCase
from app.aplicacion.poliza.use_cases.reactivar_poliza import ReactivarPolizaUseCase
from app.aplicacion.poliza.use_cases.registrar_poliza_a_proceso_comercial import RegistrarPolizaAProcesoComercialUseCase
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.aplicacion.notificacion.use_cases.generar_alerta_renovacion_poliza import GenerarAlertaRenovacionPolizaUseCase
from app.infraestructura.company_seguros.repositorio_company_seguros_postgres import RepositorioCompanySegurosPostgres
from app.infraestructura.cotizacion.repositorio_cotizaciones_postgres import RepositorioCotizacionesPostgres
from app.infraestructura.notificacion.repositorio_notificaciones_postgres import RepositorioNotificacionesPostgres
from app.infraestructura.poliza.repositorio_polizas_postgres import RepositorioPolizasPostgres
from app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres import RepositorioProcesosComercialesPostgres


def get_obtener_polizas_use_case():
    repositorio_polizas = RepositorioPolizasPostgres()

    return ObtenerPolizasUseCase(
        repositorio_polizas=repositorio_polizas
    )

def get_obtener_poliza_use_case():
    authorization_service = AuthorizationServiceFactory.crear_authorization_service()
    repositorio_polizas = RepositorioPolizasPostgres()
    
    return ObtenerPolizaUseCase(
        authorization_service=authorization_service,
        repositorio_polizas=repositorio_polizas
    )

def get_registrar_renovacion_cotizada_use_case():
    authorization_service = AuthorizationServiceFactory.crear_authorization_service()
    repositorio_polizas = RepositorioPolizasPostgres()
    repositorio_cotizaciones = RepositorioCotizacionesPostgres()

    return RegistrarRenovacionCotizadaUseCase(
        authorization_service=authorization_service,
        repositorio_cotizaciones=repositorio_cotizaciones,
        repositorio_polizas=repositorio_polizas
    )

def get_registrar_poliza_a_proceso_comercial_use_case():
    authorization_service = AuthorizationServiceFactory.crear_authorization_service()
    repositorio_polizas = RepositorioPolizasPostgres()
    repositorio_procesos_comerciales = RepositorioProcesosComercialesPostgres()
    repositorio_companies = RepositorioCompanySegurosPostgres()


    return RegistrarPolizaAProcesoComercialUseCase(
        repositorio_polizas=repositorio_polizas,
        repositorio_companies=repositorio_companies,
        repositorio_procesos_comerciales=repositorio_procesos_comerciales,
        authorization_service=authorization_service,
        repositorio_notificaciones=RepositorioNotificacionesPostgres(),
        servicio_alertas=ServicioAlertasProceso(RepositorioNotificacionesPostgres())
    )


def get_cancelar_poliza_use_case():
    repositorio_polizas = RepositorioPolizasPostgres()

    return CancelarPolizaUseCase(
        repositorio_polizas=repositorio_polizas,
        servicio_alertas=ServicioAlertasProceso(RepositorioNotificacionesPostgres()),
    )


def get_reactivar_poliza_use_case():
    repositorio_polizas = RepositorioPolizasPostgres()

    return ReactivarPolizaUseCase(
        repositorio_polizas=repositorio_polizas,
        generar_alerta_renovacion=GenerarAlertaRenovacionPolizaUseCase(
            RepositorioNotificacionesPostgres()
        ),
    )


def get_actualizar_poliza_use_case():
    authorization_service = AuthorizationServiceFactory.crear_authorization_service()
    repositorio_polizas = RepositorioPolizasPostgres()

    return ActualizarPolizaUseCase(
        repositorio_polizas=repositorio_polizas,
        authorization_service=authorization_service,
        servicio_alertas=ServicioAlertasProceso(RepositorioNotificacionesPostgres()),
        generar_alerta_renovacion=GenerarAlertaRenovacionPolizaUseCase(
            RepositorioNotificacionesPostgres()
        ),
    )


def get_iniciar_renovacion_poliza_use_case():
    authorization_service = AuthorizationServiceFactory.crear_authorization_service()
    repositorio_polizas = RepositorioPolizasPostgres()
    repositorio_procesos_comerciales = RepositorioProcesosComercialesPostgres()

    return IniciarRenovacionPolizaUseCase(
        repositorio_polizas=repositorio_polizas,
        repositorio_procesos_comerciales=repositorio_procesos_comerciales,
        authorization_service=authorization_service,
        servicio_alertas=ServicioAlertasProceso(RepositorioNotificacionesPostgres()),
    )