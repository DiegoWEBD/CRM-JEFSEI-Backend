from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.proceso_comercial.use_cases.calcular_desglose_reconstruccion_unidades import CalcularDesgloseReconstruccionUnidadesUseCase
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.solicitud_cotizacion.repositorio_unidades_alicuotas import RepositorioUnidadesAlicuotas
from app.dominio.usuario.usuario import Usuario
from app.infraestructura.solicitud_cotizacion.generador_excel_desglose_reconstruccion import GeneradorExcelDesgloseReconstruccion


class GenerarExcelDesgloseReconstruccionUnidadesUseCase:
    """Genera el Excel con el desglose de reconstrucción por unidad de una oportunidad.

    El desglose se calcula al momento: siempre refleja los datos actuales del
    condominio.
    """

    def __init__(
        self,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_unidades: RepositorioUnidadesAlicuotas,
        calcular_desglose_reconstruccion: CalcularDesgloseReconstruccionUnidadesUseCase,
        authorization_service: AuthorizationService,
        generador_excel: GeneradorExcelDesgloseReconstruccion | None = None,
    ) -> None:
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.repositorio_unidades = repositorio_unidades
        self.calcular_desglose_reconstruccion = calcular_desglose_reconstruccion
        self.authorization_service = authorization_service
        self.generador_excel = generador_excel or GeneradorExcelDesgloseReconstruccion()

    def ejecutar(self, id_proceso_comercial: int, usuario: Usuario) -> str:
        proceso = self.repositorio_procesos_comerciales.buscar(id_proceso_comercial)

        if not proceso or not proceso.id:
            raise RecursoNoEncontradoException('Oportunidad no encontrada')

        if not self.authorization_service.usuario_puede_ver_solicitudes_cotizacion(usuario, proceso.id):
            raise UsuarioNoAutorizadoException

        unidades = sorted(
            self.repositorio_unidades.listar_por_oportunidad(proceso.id),
            key=lambda u: u.fila_origen,
        )

        if not unidades:
            raise ConflictoEnAccionException('La oportunidad no tiene alícuota importada')

        desglose, total = self.calcular_desglose_reconstruccion.ejecutar(proceso.id_prospecto, unidades)

        if desglose is None:
            raise ConflictoEnAccionException(
                'El desglose de reconstrucción no se puede calcular, complete los datos de reconstrucción del prospecto'
            )

        encabezado = {
            'cliente': proceso.nombre_cliente,
            'cantidad_unidades': len(desglose),
            'monto_asegurado_sugerido_total': total,
        }

        return self.generador_excel.generar(proceso.id, desglose, encabezado)
