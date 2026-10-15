from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.proyeccion.servicios.servicio_proyecciones_comerciales import ServicioProyeccionesComerciales
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos


class ObtenerProcesosComercialesUseCase:

    def __init__(
        self, 
        authorization_service: AuthorizationService,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_prospectos: RepositorioProspectos,
        servicio_proyecciones_comerciales: ServicioProyeccionesComerciales
    ):
        self.authorization_service = authorization_service
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.repositorio_prospectos = repositorio_prospectos
        self.servicio_proyecciones_comerciales = servicio_proyecciones_comerciales

    def ejecutar(self, id_prospecto: int, rut_usuario: str | None = None, abiertos: bool | None = None) -> list[ProcesoComercial]:

        prospecto = self.repositorio_prospectos.buscar(id_prospecto)

        if not prospecto or not prospecto.id:
            raise RecursoNoEncontradoException('Prospecto no encontrado')
        
        if rut_usuario and not self.authorization_service.usuario_puede_ver_procesos_comerciales(rut_usuario, prospecto.id):
            raise UsuarioNoAutorizadoException

        procesos = self.repositorio_procesos_comerciales.obtener_procesos_comerciales(prospecto.id, abiertos)

        for proceso in procesos:
            proceso.prima_cotizada = self.servicio_proyecciones_comerciales.prima_cotizada(proceso)
            proceso.prima_potencial_estimada = self.servicio_proyecciones_comerciales.prima_potencial_estimada(proceso)
            proceso.prima_esperada = self.servicio_proyecciones_comerciales.prima_esperada(proceso)

        return procesos