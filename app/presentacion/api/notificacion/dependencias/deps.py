from app.aplicacion.notificacion.use_cases.generar_alertas_sla import GenerarAlertasSlaUseCase
from app.aplicacion.notificacion.use_cases.marcar_notificacion_leida import MarcarNotificacionLeidaUseCase
from app.aplicacion.notificacion.use_cases.marcar_notificaciones_leidas import MarcarNotificacionesLeidasUseCase
from app.aplicacion.notificacion.use_cases.obtener_contador_no_leidas import ObtenerContadorNoLeidasUseCase
from app.aplicacion.notificacion.use_cases.obtener_notificaciones import ObtenerNotificacionesUseCase
from app.aplicacion.notificacion.use_cases.obtener_oportunidades_en_riesgo import ObtenerOportunidadesEnRiesgoUseCase
from app.infraestructura.notificacion.repositorio_notificaciones_postgres import RepositorioNotificacionesPostgres
from app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres import RepositorioProcesosComercialesPostgres


def get_generar_alertas_sla_use_case():
    repositorio = RepositorioNotificacionesPostgres()
    return GenerarAlertasSlaUseCase(repositorio)


def get_obtener_notificaciones_use_case():
    repositorio = RepositorioNotificacionesPostgres()
    return ObtenerNotificacionesUseCase(repositorio)


def get_obtener_contador_no_leidas_use_case():
    repositorio = RepositorioNotificacionesPostgres()
    return ObtenerContadorNoLeidasUseCase(repositorio)


def get_marcar_notificacion_leida_use_case():
    repositorio = RepositorioNotificacionesPostgres()
    return MarcarNotificacionLeidaUseCase(repositorio)


def get_marcar_notificaciones_leidas_use_case():
    repositorio = RepositorioNotificacionesPostgres()
    return MarcarNotificacionesLeidasUseCase(repositorio)


def get_obtener_oportunidades_en_riesgo_use_case():
    repositorio = RepositorioProcesosComercialesPostgres()
    return ObtenerOportunidadesEnRiesgoUseCase(repositorio)
