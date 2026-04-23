from fastapi import FastAPI
from app.presentacion.api.auth import auth_router
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
app.include_router(usuario_router.router)