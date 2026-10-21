from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.proceso_comercial.use_cases.calcular_desglose_reconstruccion_unidades import CalcularDesgloseReconstruccionUnidadesUseCase
from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.cotizacion.repositorio_cotizaciones import RepositorioCotizaciones
from app.dominio.estudio_comercial.desglose_unidades.calculadora_desglose_unidades import CalculadoraDesgloseUnidades
from app.dominio.estudio_comercial.desglose_unidades.desglose_unidad import DesgloseUnidad
from app.dominio.estudio_comercial.desglose_unidades.totales_prima import TotalesPrima
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion
from app.dominio.solicitud_cotizacion.repositorio_unidades_alicuotas import RepositorioUnidadesAlicuotas
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.desglose_reconstruccion_unidad import DesgloseReconstruccionUnidad
from app.infraestructura.estudio_comercial_condominio.generador_excel_desglose_unidades import GeneradorExcelDesgloseUnidades


class GenerarDesgloseUnidadesUseCase:
    """Genera el Excel con el desglose por unidad de las cotizaciones de una solicitud de tipo 'unidades'.

    El cálculo de primas se hace una única vez por cotización sobre el monto
    asegurado sugerido total (la suma de los montos redondeados a la centena
    superior); cada prima se reparte luego por el `prorrateo_pago` de cada
    unidad (monto asegurado sugerido de la unidad sobre el total sugerido).
    """

    def __init__(
        self,
        authorization_service: AuthorizationService,
        repositorio_solicitudes: RepositorioSolicitudesCotizacion,
        repositorio_unidades: RepositorioUnidadesAlicuotas,
        repositorio_cotizaciones: RepositorioCotizaciones,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        calcular_desglose_reconstruccion: CalcularDesgloseReconstruccionUnidadesUseCase,
        generador_excel: GeneradorExcelDesgloseUnidades | None = None,
    ) -> None:
        self.authorization_service = authorization_service
        self.repositorio_solicitudes = repositorio_solicitudes
        self.repositorio_unidades = repositorio_unidades
        self.repositorio_cotizaciones = repositorio_cotizaciones
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.calcular_desglose_reconstruccion = calcular_desglose_reconstruccion
        self.generador_excel = generador_excel or GeneradorExcelDesgloseUnidades()

    def ejecutar(self, id_solicitud: int, ids_cotizacion: list[int], rut_usuario: str | None) -> str:
        if not ids_cotizacion:
            raise ConflictoEnAccionException('No se puede generar el desglose por unidad sin cotizaciones')

        solicitud = self.repositorio_solicitudes.buscar(id_solicitud)

        if not solicitud or not solicitud.id:
            raise RecursoNoEncontradoException('Solicitud no encontrada')

        if rut_usuario is not None and not self.authorization_service.usuario_puede_ver_solicitud_cotizacion(
            rut_usuario, solicitud.id
        ):
            raise UsuarioNoAutorizadoException

        if solicitud.tipo != 'unidades':
            raise ConflictoEnAccionException('El desglose por unidad solo aplica a solicitudes de la línea unidades')

        if solicitud.monto_asegurado is None:
            raise ConflictoEnAccionException('La solicitud no tiene monto asegurado registrado')

        proceso = self.repositorio_procesos_comerciales.buscar_por_solicitud_cotizacion(id_solicitud)

        if proceso is None or proceso.id is None:
            raise RecursoNoEncontradoException('Oportunidad de la solicitud no encontrada')

        unidades = sorted(
            self.repositorio_unidades.listar_por_oportunidad(proceso.id),
            key=lambda u: u.fila_origen,
        )

        if not unidades:
            raise ConflictoEnAccionException('La oportunidad no tiene alícuota importada')

        desglose_reconstruccion, total_sugerido = self.calcular_desglose_reconstruccion.ejecutar(
            proceso.id_prospecto, unidades
        )

        if desglose_reconstruccion is None:
            raise ConflictoEnAccionException(
                'El desglose de reconstrucción de las unidades no se puede calcular, complete los datos de reconstrucción del prospecto'
            )

        if total_sugerido is None or total_sugerido <= 0:
            raise ConflictoEnAccionException('El monto asegurado sugerido total de las unidades debe ser mayor a cero')

        cotizaciones = self.__buscar_cotizaciones(ids_cotizacion, id_solicitud)

        datos = [
            self.__detalle_cotizacion(cotizacion, desglose_reconstruccion)
            for cotizacion in cotizaciones
        ]

        return self.generador_excel.generar(id_solicitud, datos)

    def __buscar_cotizaciones(self, ids_cotizacion: list[int], id_solicitud: int) -> list[Cotizacion]:
        cotizaciones: list[Cotizacion] = []

        for id_cotizacion in ids_cotizacion:
            cotizacion = self.repositorio_cotizaciones.obtener_por_id(id_cotizacion)

            if cotizacion is None:
                raise RecursoNoEncontradoException(f'Cotización {id_cotizacion} no encontrada')

            if not self.repositorio_cotizaciones.cotizacion_pertenece_a_solicitud(cotizacion, id_solicitud):
                raise ConflictoEnAccionException(
                    f'La cotización {id_cotizacion} no pertenece a la solicitud {id_solicitud}'
                )

            cotizaciones.append(cotizacion)

        return cotizaciones

    def __detalle_cotizacion(
        self,
        cotizacion: Cotizacion,
        desglose_reconstruccion: list[DesgloseReconstruccionUnidad],
    ) -> tuple[Cotizacion, TotalesPrima, list[DesgloseUnidad]]:
        totales = CalculadoraDesgloseUnidades.calcular_totales(cotizacion)
        desglose = CalculadoraDesgloseUnidades.calcular_desglose_unidades(cotizacion, desglose_reconstruccion)

        return cotizacion, totales, desglose
