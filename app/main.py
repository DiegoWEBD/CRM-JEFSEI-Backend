from fastapi import Depends, FastAPI
from app.presentacion.api.auth import auth_router
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
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