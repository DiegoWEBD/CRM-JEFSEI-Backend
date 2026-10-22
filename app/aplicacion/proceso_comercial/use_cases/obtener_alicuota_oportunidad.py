from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.unidades.repositorio_unidades_alicuotas import RepositorioUnidadesAlicuotas
from app.dominio.unidades.unidad_alicuota import UnidadAlicuota
from app.dominio.usuario.usuario import Usuario


class ObtenerAlicuotaOportunidadUseCase:

    def __init__(
        self,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_unidades: RepositorioUnidadesAlicuotas,
        authorization_service: AuthorizationService,
    ) -> None:
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.repositorio_unidades = repositorio_unidades
        self.authorization_service = authorization_service

    def ejecutar(
        self,
        id_proceso_comercial: int,
        usuario: Usuario,
    ) -> tuple[str | None, list[UnidadAlicuota]]:
        proceso = self.repositorio_procesos_comerciales.buscar(id_proceso_comercial)

        if not proceso or not proceso.id:
            raise RecursoNoEncontradoException('Oportunidad no encontrada')

        if not self.authorization_service.usuario_puede_ver_solicitudes_cotizacion(usuario, proceso.id):
            raise UsuarioNoAutorizadoException

        nombre_excel = self.repositorio_unidades.obtener_nombre_excel(proceso.id)
        unidades = self.repositorio_unidades.listar_por_oportunidad(proceso.id)

        return nombre_excel, unidades
