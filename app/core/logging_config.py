# app/core/logging_config.py
"""Logging técnico con correlación contra la tabla de auditoría.

El objetivo es que una línea de log, un evento de ``auditoria_evento`` y el
log de NGINX se pueda unir por ``request_id``.
"""

import logging
import logging.config
import sys

from app.core.contextos import obtener_request_id

LOG_FORMAT = '%(asctime)s %(levelname)-8s %(name)s request_id=%(request_id)s %(message)s'


class RequestIdFilter(logging.Filter):
    """Inyecta el request_id del ContextVar. Si no hay, deja ``-``."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = obtener_request_id() or '-'
        return True


def configurar_logging() -> None:
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'request_id': {'()': RequestIdFilter},
        },
        'formatters': {
            'estandar': {
                'format': LOG_FORMAT,
                'datefmt': '%Y-%m-%dT%H:%M:%S%z',
            },
        },
        'handlers': {
            'consola': {
                'class': 'logging.StreamHandler',
                'stream': sys.stdout,
                'formatter': 'estandar',
                'filters': ['request_id'],
            },
        },
        'root': {
            'level': 'INFO',
            'handlers': ['consola'],
        },
        'loggers': {
            'app': {'level': 'INFO', 'propagate': True},
            # uvicorn ya tiene su propio formato; se sube a WARNING para no
            # duplicar cada request en dos estilos distintos.
            'uvicorn.access': {'level': 'WARNING', 'propagate': False},
        },
    })
