from fastapi import Depends, FastAPI
from app.presentacion.api.auth import auth_router
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.comuna import comuna_router
from app.presentacion.api.estudio_comercial import estudio_comercial_router
from app.presentacion.api.linea_negocio import linea_negocio_router
from app.presentacion.api.prospecto import prospecto_router
from app.presentacion.api.usuario import usuario_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CRM JEFSEI API",
    version="1.0.0"
)

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    router=estudio_comercial_router.router,
    dependencies=[
        Depends(get_current_user)
    ]
)