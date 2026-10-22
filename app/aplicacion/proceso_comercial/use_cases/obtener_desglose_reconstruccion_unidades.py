from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.proceso_comercial.use_cases.calcular_desglose_reconstruccion_unidades import CalcularDesgloseReconstruccionUnidadesUseCase
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.unidades.repositorio_unidades_alicuotas import RepositorioUnidadesAlicuotas
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.desglose_reconstruccion_unidad import DesgloseReconstruccionUnidad
from app.dominio.usuario.usuario import Usuario


class ObtenerDesgloseReconstruccionUnidadesUseCase:
    """Devuelve el desglose de reconstrucción de una oportunidad, calculado al momento."""

    def __init__(
        self,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_unidades: RepositorioUnidadesAlicuotas,
        calcular_desglose_reconstruccion: CalcularDesgloseReconstruccionUnidadesUseCase,
        authorization_service: AuthorizationService,
    ) -> None:
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.repositorio_unidades = repositorio_unidades
        self.calcular_desglose_reconstruccion = calcular_desglose_reconstruccion
        self.authorization_service = authorization_service

    def ejecutar(
        self,
        id_proceso_comercial: int,
        usuario: Usuario,
    ) -> tuple[float | None, list[DesgloseReconstruccionUnidad]]:
        proceso = self.repositorio_procesos_comerciales.buscar(id_proceso_comercial)

        if not proceso or not proceso.id:
            raise RecursoNoEncontradoException('Oportunidad no encontrada')

        if not self.authorization_service.usuario_puede_ver_solicitudes_cotizacion(usuario, proceso.id):
            raise UsuarioNoAutorizadoException

        unidades = self.repositorio_unidades.listar_por_oportunidad(proceso.id)
        desglose, total = self.calcular_desglose_reconstruccion.ejecutar(proceso.id_prospecto, unidades)

        return total, desglose or []
