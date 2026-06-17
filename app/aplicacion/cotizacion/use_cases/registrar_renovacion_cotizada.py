from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.cotizacion.repositorio_cotizaciones import RepositorioCotizaciones
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas


class RegistrarRenovacionCotizadaUseCase:

    def __init__(
        self,
        authorization_service: AuthorizationService,
        repositorio_polizas: RepositorioPolizas,
        repositorio_cotizaciones: RepositorioCotizaciones,
    ):
        self.authorization_service = authorization_service
        self.repositorio_polizas = repositorio_polizas
        self.repositorio_cotizaciones = repositorio_cotizaciones

    def ejecutar(self, numero_poliza: str, rut_usuario: str):

        poliza = self.repositorio_polizas.buscar(numero_poliza)

        if not poliza:
            raise RecursoNoEncontradoException(f'Póliza {numero_poliza} no encontrada')
        
        if not self.authorization_service.usuario_puede_gestionar_renovacion(rut_usuario, numero_poliza):
            raise UsuarioNoAutorizadoException
        
        self.repositorio_cotizaciones.registrar_renovacion_cotizada(numero_poliza)