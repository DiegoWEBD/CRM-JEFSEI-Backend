from app.aplicacion.auth.use_cases.iniciar_sesion import IniciarSesionUseCase
from app.infraestructura.usuario.repositorio_usuarios_impl import RepositorioUsuariosImpl


def obtener_caso_de_uso_iniciar_sesion():
    repositorio = RepositorioUsuariosImpl()
    yield IniciarSesionUseCase(repositorio)