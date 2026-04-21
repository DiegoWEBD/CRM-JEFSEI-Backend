from app.aplicacion.auth.use_cases.iniciar_sesion import IniciarSesionUseCase
from app.infraestructura.usuario.repositorio_usuarios_postgres import RepositorioUsuariosPostgres


def obtener_caso_de_uso_iniciar_sesion():
    repositorio = RepositorioUsuariosPostgres()
    yield IniciarSesionUseCase(repositorio)