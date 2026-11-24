from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.gestion_comercial.gestion_comercial import GestionComercial
from app.dominio.gestion_comercial.repositorio_gestiones_comerciales import RepositorioGestionesComerciales
from app.dominio.usuario.usuario import Usuario


class ObtenerGestionesComercialesUseCase:

    def __init__(
        self,
        repositorio: RepositorioGestionesComerciales,
        authorization_service: AuthorizationService,
    ) -> None:
        self.repositorio = repositorio
        self.authorization_service = authorization_service

    def ejecutar(self, usuario: Usuario, id_prospecto: int | None = None) -> list[GestionComercial]:
        if id_prospecto is not None:
            if not self.authorization_service.usuario_puede_ver_gestiones_comerciales_prospecto(usuario, id_prospecto):
                raise UsuarioNoAutorizadoException(
                    'No tiene permiso para ver las gestiones de este prospecto'
                )
            return self.repositorio.obtener_todas(id_prospecto=id_prospecto)

        if self.authorization_service.usuario_puede_ver_todas_las_gestiones_comerciales(usuario):
            return self.repositorio.obtener_todas()

        return self.repositorio.obtener_todas(rut_usuario=usuario.rut)
