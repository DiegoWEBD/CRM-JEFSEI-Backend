from fastapi import FastAPI
from app.presentacion.api import auth

app = FastAPI(
    title="CRM JEFSEI API",
    version="1.0.0"
)

app.include_router(auth.router, prefix="/api")