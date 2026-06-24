from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.usuario import Usuario


class CrearProcesoComercialUseCase:

    def __init__(
        self,
        authorization_service: AuthorizationService,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_prospectos: RepositorioProspectos
    ) -> None:
        self.authorization_service = authorization_service
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.repositorio_prospectos = repositorio_prospectos

    def ejecutar(self, tipo: str, id_prospecto: int, usuario: Usuario) -> ProcesoComercial:
        print(id_prospecto)
        prospecto = self.repositorio_prospectos.buscar(id_prospecto)
        print(prospecto)

        if not prospecto:
            raise RecursoNoEncontradoException('Prospecto no encontrado')
        
        if not self.authorization_service.usuario_puede_crear_proceso_comercial(usuario, id_prospecto):
            raise UsuarioNoAutorizadoException
        
        id_nuevo_proceso = self.repositorio_procesos_comerciales.nuevo(
            tipo=tipo,
            id_prospecto=id_prospecto,
            rut_usuario=usuario.rut
        )

        if id_nuevo_proceso is None:
            raise Exception('Error al crear una nueva oportunidad comercial')
        
        proceso = self.repositorio_procesos_comerciales.buscar(id_nuevo_proceso)

        if not proceso:
            raise Exception('Error al crear una nueva oportunidad comercial')
        
        return proceso