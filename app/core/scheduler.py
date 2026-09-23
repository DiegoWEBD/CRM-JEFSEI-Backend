import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.aplicacion.notificacion.use_cases.generar_alertas_sla import GenerarAlertasSlaUseCase
from app.core.config import settings
from app.infraestructura.notificacion.repositorio_notificaciones_postgres import RepositorioNotificacionesPostgres

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def generar_alertas_sla_job() -> None:
    try:
        use_case = GenerarAlertasSlaUseCase(RepositorioNotificacionesPostgres())
        creadas = use_case.ejecutar()
        if creadas:
            logger.info('Generadas %s alertas SLA', len(creadas))
    except Exception:
        logger.exception('Error generando alertas SLA')


def iniciar_scheduler() -> BackgroundScheduler | None:
    global _scheduler

    if not settings.CRM_INICIAR_SCHEDULER:
        logger.info('Scheduler de alertas deshabilitado (CRM_INICIAR_SCHEDULER=false)')
        return None

    if _scheduler is not None:
        return _scheduler

    _scheduler = BackgroundScheduler(timezone='UTC')
    _scheduler.add_job(
        generar_alertas_sla_job,
        trigger=IntervalTrigger(minutes=settings.CRM_SCHEDULER_INTERVALO_MINUTOS),
        id='generar_alertas_sla',
        replace_existing=True,
        max_instances=1,
    )
    _scheduler.start()
    logger.info(
        'Scheduler de alertas iniciado (cada %s min)',
        settings.CRM_SCHEDULER_INTERVALO_MINUTOS,
    )
    return _scheduler


def detener_scheduler() -> None:
    global _scheduler

    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info('Scheduler de alertas detenido')
