from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.cotizacion.repositorio_cotizaciones import RepositorioCotizaciones
from app.dominio.estudio_comercial.desglose_unidades.calculadora_desglose_unidades import CalculadoraDesgloseUnidades
from app.dominio.estudio_comercial.desglose_unidades.desglose_unidad import DesgloseUnidad
from app.dominio.estudio_comercial.desglose_unidades.totales_prima import TotalesPrima
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.prospecto.prospecto_condominio.servicio_calculo_reconstruccion import ServicioCalculoReconstruccion
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion
from app.dominio.solicitud_cotizacion.repositorio_unidades_alicuotas import RepositorioUnidadesAlicuotas
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.unidad_alicuota import UnidadAlicuota
from app.infraestructura.estudio_comercial_condominio.generador_excel_desglose_unidades import GeneradorExcelDesgloseUnidades


class GenerarDesgloseUnidadesUseCase:
    """Genera el Excel con el desglose por unidad de las cotizaciones de una solicitud de tipo 'unidades'.

    Dos hojas: una con el monto asegurado de la solicitud y otra con el monto
    sugerido (unidades del valor de reconstrucción depreciado del prospecto).
    """

    def __init__(
        self,
        authorization_service: AuthorizationService,
        repositorio_solicitudes: RepositorioSolicitudesCotizacion,
        repositorio_unidades: RepositorioUnidadesAlicuotas,
        repositorio_cotizaciones: RepositorioCotizaciones,
        repositorio_prospectos: RepositorioProspectos,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        generador_excel: GeneradorExcelDesgloseUnidades | None = None,
    ) -> None:
        self.authorization_service = authorization_service
        self.repositorio_solicitudes = repositorio_solicitudes
        self.repositorio_unidades = repositorio_unidades
        self.repositorio_cotizaciones = repositorio_cotizaciones
        self.repositorio_prospectos = repositorio_prospectos
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
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

        cotizaciones = self.__buscar_cotizaciones(ids_cotizacion, id_solicitud)
        monto_sugerido = self.__calcular_monto_sugerido(id_solicitud)

        datos_actual = [
            self.__detalle_cotizacion(cotizacion, unidades, solicitud.monto_asegurado)
            for cotizacion in cotizaciones
        ]
        datos_sugerido = [
            self.__detalle_cotizacion(cotizacion, unidades, monto_sugerido)
            for cotizacion in cotizaciones
        ]

        return self.generador_excel.generar(id_solicitud, datos_actual, datos_sugerido)

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

    def __calcular_monto_sugerido(self, id_solicitud: int) -> float:
        id_prospecto = self.repositorio_solicitudes.buscar_id_prospecto_de_solicitud(id_solicitud)

        if id_prospecto is None:
            raise RecursoNoEncontradoException('Prospecto de la solicitud no encontrado')

        prospecto = self.repositorio_prospectos.buscar_prospecto_condominio(id_prospecto)

        if prospecto is None:
            raise ConflictoEnAccionException('El prospecto de la solicitud no tiene datos de condominio')

        if prospecto.metros_cuadrados is None:
            raise ConflictoEnAccionException('No se puede calcular el monto sugerido, faltan los metros cuadrados')

        if prospecto.uf_por_metro_cuadrado is None:
            raise ConflictoEnAccionException('No se puede calcular el monto sugerido, falta el valor de la UF / m²')

        if prospecto.porcentaje_depreciacion is None:
            raise ConflictoEnAccionException('No se puede calcular el monto sugerido, falta el porcentaje de depreciación')

        valor_reconstruccion = ServicioCalculoReconstruccion.calcular_valor_reconstruccion(
            prospecto.uf_por_metro_cuadrado, prospecto.metros_cuadrados
        )
        valor_reconstruccion_depreciacion = ServicioCalculoReconstruccion.calcular_valor_reconstruccion_depreciacion(
            valor_reconstruccion, prospecto.porcentaje_depreciacion
        )

        return ServicioCalculoReconstruccion.calcular_valor_unidades(valor_reconstruccion_depreciacion)

    def __detalle_cotizacion(
        self,
        cotizacion: Cotizacion,
        unidades: list[UnidadAlicuota],
        monto_base: float,
    ) -> tuple[Cotizacion, TotalesPrima, list[DesgloseUnidad]]:
        totales = CalculadoraDesgloseUnidades.calcular_totales(cotizacion, monto_base)
        desglose = CalculadoraDesgloseUnidades.calcular_desglose(totales, unidades)

        return cotizacion, totales, desglose
