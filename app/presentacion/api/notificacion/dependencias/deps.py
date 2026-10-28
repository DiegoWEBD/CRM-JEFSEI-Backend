from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.aplicacion.notificacion.use_cases.generar_alertas_sla import GenerarAlertasSlaUseCase
from app.aplicacion.notificacion.use_cases.marcar_notificacion_leida import MarcarNotificacionLeidaUseCase
from app.aplicacion.notificacion.use_cases.marcar_notificaciones_leidas import MarcarNotificacionesLeidasUseCase
from app.aplicacion.notificacion.use_cases.obtener_contador_notificaciones import ObtenerContadorNotificacionesUseCase
from app.aplicacion.notificacion.use_cases.obtener_notificaciones import ObtenerNotificacionesUseCase
from app.infraestructura.notificacion.repositorio_notificaciones_postgres import RepositorioNotificacionesPostgres


def get_generar_alertas_sla_use_case():
    repositorio = RepositorioNotificacionesPostgres()
    return GenerarAlertasSlaUseCase(repositorio, ServicioAlertasProceso(repositorio))


def get_obtener_notificaciones_use_case():
    repositorio = RepositorioNotificacionesPostgres()
    return ObtenerNotificacionesUseCase(repositorio)


def get_obtener_contador_notificaciones_use_case():
    repositorio = RepositorioNotificacionesPostgres()
    return ObtenerContadorNotificacionesUseCase(repositorio)


def get_marcar_notificacion_leida_use_case():
    repositorio = RepositorioNotificacionesPostgres()
    return MarcarNotificacionLeidaUseCase(repositorio)


def get_marcar_notificaciones_leidas_use_case():
    repositorio = RepositorioNotificacionesPostgres()
    return MarcarNotificacionesLeidasUseCase(repositorio)
