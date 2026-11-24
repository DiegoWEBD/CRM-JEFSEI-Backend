from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.gestion_comercial.gestion_comercial import GestionComercial
from app.dominio.gestion_comercial.repositorio_gestiones_comerciales import RepositorioGestionesComerciales
from app.dominio.usuario.usuario import Usuario


class ObtenerUltimaGestionComercialUseCase:

    def __init__(
        self,
        repositorio: RepositorioGestionesComerciales,
        authorization_service: AuthorizationService,
    ) -> None:
        self.repositorio = repositorio
        self.authorization_service = authorization_service

    def ejecutar(self, usuario: Usuario, id_prospecto: int) -> GestionComercial | None:
        if not self.authorization_service.usuario_puede_ver_gestiones_comerciales_prospecto(usuario, id_prospecto):
            raise UsuarioNoAutorizadoException(
                'No tiene permiso para ver las gestiones de este prospecto'
            )

        return self.repositorio.obtener_ultima(id_prospecto=id_prospecto)
