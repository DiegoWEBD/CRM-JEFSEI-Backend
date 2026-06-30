from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.presentacion.api.administrador_condominio import administrador_condominio_router
from app.presentacion.api.auth import auth_router
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.comuna import comuna_router
from app.presentacion.api.company_seguros import company_seguros_router
from app.presentacion.api.comunicado_gerencia import comunicado_gerencia_router
from app.presentacion.api.estudio_comercial import estudio_comercial_router
from app.presentacion.api.exceptions.bad_request_exception import BadRequestException
from app.presentacion.api.linea_negocio import linea_negocio_router
from app.presentacion.api.metricas import metricas_router
from app.presentacion.api.poliza import poliza_router
from app.presentacion.api.proceso_comercial import proceso_comercial_router
from app.presentacion.api.prospecto import prospecto_router
from app.presentacion.api.recordatorio import recordatorio_router
from app.presentacion.api.solicitud_cotizacion import solicitud_cotizacion_router
from app.presentacion.api.sucursal import sucursal_router
from app.presentacion.api.usuario import usuario_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title='CRM JEFSEI API',
    version='1.0.0'
)

origins = [
    'http://localhost:3000',
    'http://localhost:3001'
]

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
    _: Request,
    exc: Exception,
):
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