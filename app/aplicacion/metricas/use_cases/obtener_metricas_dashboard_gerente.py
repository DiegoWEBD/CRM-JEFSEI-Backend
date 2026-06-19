from datetime import date, datetime

from app.aplicacion.metricas.dto.metricas_dashboard_gerente_dto import (
    ActividadTipoDto,
    ActividadesComercialesDto,
    CompaniaTopDto,
    EvaluacionProyectosDto,
    ItemCantidadDto,
    ItemValorDto,
    KpisEvaluacionDto,
    MesActualDto,
    MetricasDashboardGerenteDto,
    ProduccionDto,
    ReportesPolizasDto,
    ResumenActividadesDto,
    TendenciaMesDto,
)
from app.dominio.metricas.repositorio_metricas_dashboard import (
    RepositorioMetricasDashboard,
)

MESES_ES: dict[int, str] = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}


class ObtenerMetricasDashboardGerenteUseCase:

    def __init__(
        self,
        repositorio: RepositorioMetricasDashboard,
    ):
        self.repositorio = repositorio

    def ejecutar(self) -> MetricasDashboardGerenteDto:
        hoy = date.today()
        anio = hoy.year
        mes = hoy.month

        return MetricasDashboardGerenteDto(
            produccion=self._armar_produccion(anio, mes, hoy),
            actividades_comerciales=self._armar_actividades(anio, mes),
            reportes_polizas=self._armar_reportes_polizas(),
            evaluacion_proyectos=self._armar_evaluacion_proyectos(),
        )

    def _armar_produccion(
        self, anio: int, mes: int, hoy: date
    ) -> ProduccionDto:
        mes_actual = self.repositorio.obtener_prima_neta_mes(anio, mes)

        mes_anterior = mes - 1 if mes > 1 else 12
        anio_anterior = anio if mes > 1 else anio - 1
        prima_mes_anterior = self.repositorio.obtener_prima_neta_mes(
            anio_anterior, mes_anterior
        )

        variacion = (
            round(
                (mes_actual - prima_mes_anterior)
                / prima_mes_anterior
                * 100,
                1,
            )
            if prima_mes_anterior > 0
            else 0.0
        )

        mes_label = f"{MESES_ES[mes]} {anio}"

        tendencia_raw = self.repositorio.obtener_tendencia_12_meses()
        tendencia = [
            TendenciaMesDto(mes=r["mes"], prima_neta=float(r["prima_neta"]))
            for r in tendencia_raw
        ]

        por_compania_raw = self.repositorio.obtener_prima_por_compania(
            anio, mes
        )
        por_compania = [
            ItemValorDto(nombre=r["nombre"], valor=float(r["valor"]))
            for r in por_compania_raw
        ]

        por_ejecutivo_raw = self.repositorio.obtener_prima_por_ejecutivo(
            anio, mes
        )
        por_ejecutivo = [
            ItemValorDto(nombre=r["nombre"], valor=float(r["valor"]))
            for r in por_ejecutivo_raw
        ]

        por_ramo_raw = self.repositorio.obtener_prima_por_producto(
            anio, mes
        )
        por_ramo = [
            ItemValorDto(nombre=r["nombre"], valor=float(r["valor"]))
            for r in por_ramo_raw
        ]

        compania_top = (
            CompaniaTopDto(
                nombre=por_compania[0].nombre,
                prima_neta=por_compania[0].valor,
            )
            if por_compania
            else None
        )

        return ProduccionDto(
            mes_actual=MesActualDto(
                total_prima_neta=mes_actual,
                variacion_mes_anterior=variacion,
                mes_label=mes_label,
            ),
            tendencia_12_meses=tendencia,
            por_compania=por_compania,
            por_ejecutivo=por_ejecutivo,
            por_ramo=por_ramo,
            compania_top=compania_top,
        )

    def _armar_actividades(
        self, anio: int, mes: int
    ) -> ActividadesComercialesDto:
        por_tipo_raw = self.repositorio.obtener_actividades_comerciales(
            anio, mes
        )
        por_tipo = [
            ActividadTipoDto(
                tipo=r["tipo"],
                concretadas=r["concretadas"],
                pendientes=r["pendientes"],
            )
            for r in por_tipo_raw
        ]

        resumen_raw = self.repositorio.obtener_resumen_actividades(anio, mes)
        resumen = ResumenActividadesDto(
            agendadas=resumen_raw["agendadas"],
            concretadas=resumen_raw["concretadas"],
            pendientes=resumen_raw["pendientes"],
            porcentaje_cumplimiento=float(
                resumen_raw["porcentaje_cumplimiento"]
            ),
        )

        return ActividadesComercialesDto(
            por_tipo=por_tipo, resumen=resumen
        )

    def _armar_reportes_polizas(self) -> ReportesPolizasDto:
        por_comuna_raw = self.repositorio.obtener_polizas_por_comuna()
        por_comuna = [
            ItemCantidadDto(nombre=r["nombre"], cantidad=r["cantidad"])
            for r in por_comuna_raw
        ]

        por_ramo_raw = self.repositorio.obtener_polizas_por_producto()
        por_ramo = [
            ItemCantidadDto(nombre=r["nombre"], cantidad=r["cantidad"])
            for r in por_ramo_raw
        ]

        return ReportesPolizasDto(
            por_comuna=por_comuna,
            por_sexo=[],
            por_rango_edad=[],
            por_ramo=por_ramo,
        )

    def _armar_evaluacion_proyectos(self) -> EvaluacionProyectosDto:
        kpis_raw = self.repositorio.obtener_kpis_evaluacion()
        kpis = KpisEvaluacionDto(
            total_proyectos=kpis_raw["total_proyectos"],
            monto_total_uf=float(kpis_raw["monto_total_uf"]),
            tasa_conversion=float(kpis_raw["tasa_conversion"]),
        )

        por_compania_raw = (
            self.repositorio.obtener_evaluacion_por_compania()
        )
        por_compania = [
            ItemCantidadDto(
                nombre=r["nombre"] or "Sin compañía",
                cantidad=r["cantidad"],
            )
            for r in por_compania_raw
        ]

        por_ramo_raw = self.repositorio.obtener_evaluacion_por_producto()
        por_ramo = [
            ItemCantidadDto(nombre=r["nombre"], cantidad=r["cantidad"])
            for r in por_ramo_raw
        ]

        return EvaluacionProyectosDto(
            kpis=kpis,
            por_compania=por_compania,
            por_ramo=por_ramo,
        )
