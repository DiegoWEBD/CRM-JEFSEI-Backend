from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.poliza.poliza import Poliza
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas
from app.dominio.usuario.usuario import Usuario


class ObtenerPolizaUseCase:

    def __init__(
        self, 
        repositorio_polizas: RepositorioPolizas,
        authorization_service: AuthorizationService
    ):
        self.repositorio_polizas = repositorio_polizas
        self.authorization_service = authorization_service

    def ejecutar(self, numero_poliza: str, usuario: Usuario) -> Poliza:
        poliza = self.repositorio_polizas.buscar(numero_poliza)
        
        if not poliza:
            raise RecursoNoEncontradoException(f'Póliza {numero_poliza} no encontrada')
        
        if not self.authorization_service.usuario_puede_ver_poliza(usuario.rut, numero_poliza):
            raise UsuarioNoAutorizadoException

        return poliza