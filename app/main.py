from fastapi import FastAPI
from app.presentacion.api.auth import auth_router
from app.presentacion.api.usuario import usuario_router

app = FastAPI(
    title="CRM JEFSEI API",
    version="1.0.0"
)

app.include_router(auth_router.router)
app.include_router(usuario_router.router)