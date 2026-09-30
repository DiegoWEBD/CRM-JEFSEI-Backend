from contextlib import asynccontextmanager

import asyncio
import logging

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.contextos import obtener_request_id
from app.core.hub_notificaciones import hub
from app.core.logging_config import configurar_logging
from app.core.scheduler import detener_scheduler, iniciar_scheduler
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.presentacion.api.administrador_condominio import administrador_condominio_router
from app.presentacion.api.archivo import archivo_router
from app.presentacion.api.auth import auth_router
from app.presentacion.api.cliente import cliente_router
from app.presentacion.api.cobranza import cobranza_router
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.comuna import comuna_router
from app.presentacion.api.company_seguros import company_seguros_router
from app.presentacion.api.comunicado_gerencia import comunicado_gerencia_router
from app.presentacion.api.configuracion_condominio import configuracion_condominio_router
from app.presentacion.api.contacto import contacto_router
from app.presentacion.api.cuota import cuota_router
from app.presentacion.api.etapa_proceso_comercial import etapa_proceso_comercial_router
from app.presentacion.api.estudio_comercial import estudio_comercial_router
from app.presentacion.api.exceptions.bad_request_exception import BadRequestException
from app.presentacion.api.gestion_comercial import gestion_comercial_router
from app.presentacion.api.linea_negocio import linea_negocio_router
from app.presentacion.api.metricas import metricas_router
from app.presentacion.api.notificacion import notificacion_router, ws_router
from app.presentacion.api.poliza import poliza_router
from app.presentacion.api.producto import producto_router
from app.presentacion.api.proceso_comercial import proceso_comercial_router
from app.presentacion.api.prospecto import prospecto_router
from app.presentacion.api.recordatorio import recordatorio_router
from app.presentacion.api.rol import rol_router
from app.presentacion.api.solicitud_cotizacion import solicitud_cotizacion_router
from app.infraestructura.auditoria.middleware_auditoria import MiddlewareAuditoria
from app.presentacion.api.sucursal import sucursal_router
from app.presentacion.api.usuario import usuario_router
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_: FastAPI):
    configurar_logging()
    # El hub de WebSockets publica desde threads (scheduler, endpoints), así que
    # necesita referencia al event loop principal.
    hub.capturar_loop(asyncio.get_running_loop())
    iniciar_scheduler()
    yield
    detener_scheduler()


app = FastAPI(
    title='CRM JEFSEI API',
    version='1.0.0',
    lifespan=lifespan,
)

origins = settings.origenes_permitidos

# La auditoría va primero (de outermost a innermost) para que el X-Request-ID
# esté disponible en toda la cadena, incluido el manejo de CORS. Se registra
# después de CORSMiddleware porque en Starlette el último agregado es el más
# externo: esto hace que el header de correlación llegue también a las
# respuestas de CORS y a los redirect.
app.add_middleware(MiddlewareAuditoria)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.exception_handler(RecursoNoEncontradoException)
async def recurso_no_encontrado_handler(
    _: Request,
    exc: RecursoNoEncontradoException,
):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'detail': str(exc)},
    )


@app.exception_handler(UsuarioNoAutorizadoException)
async def usuario_no_autorizado_handler(
    _: Request,
    exc: UsuarioNoAutorizadoException,
):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={'detail': str(exc)},
    )


@app.exception_handler(BadRequestException)
async def bad_request_handler(
    _: Request,
    exc: BadRequestException,
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': str(exc)},
    )


@app.exception_handler(RecursoYaExisteException)
async def recurso_ya_existe_handler(
    _: Request,
    exc: RecursoYaExisteException,
):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={'detail': str(exc)},
    )


@app.exception_handler(ConflictoEnAccionException)
async def conflict_handler(
    _: Request,
    exc: ConflictoEnAccionException,
):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={'detail': str(exc)},
    )


@app.exception_handler(Exception)
async def internal_server_error_handler(
    request: Request,
    exc: Exception,
):
    # Antes esto devolvía el 500 sin registrar nada, dejando los errores sin
    # rastro fuera del request_id que ahora exige la auditoría (§20, §44).
    logger.exception(
        'Error no controlado en %s %s',
        request.method,
        request.url.path,
        extra={
            'request_id': obtener_request_id() or '-',
            'metodo_http': request.method,
            'path': request.url.path,
        },
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'detail': 'Ha ocurrido un error interno en el servidor'},
    )


app.include_router(auth_router.router)

app.include_router(
    router=usuario_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=prospecto_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=contacto_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=cliente_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=linea_negocio_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=comuna_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=company_seguros_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=estudio_comercial_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=recordatorio_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=comunicado_gerencia_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=poliza_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=solicitud_cotizacion_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=metricas_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=administrador_condominio_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=proceso_comercial_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=sucursal_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=gestion_comercial_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=rol_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=cuota_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=etapa_proceso_comercial_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=cobranza_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=archivo_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=configuracion_condominio_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=producto_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

app.include_router(
    router=notificacion_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)

# El WebSocket se autentica con el ticket de /auth/ws-ticket (el navegador no
# envía la cookie de sesión en un handshake cruzado), no con Depends(get_current_user).
app.include_router(ws_router.router)