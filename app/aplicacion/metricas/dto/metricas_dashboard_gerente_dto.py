from dataclasses import dataclass, field


@dataclass
class TendenciaMesDto:
    mes: str
    prima_neta: float


@dataclass
class ItemValorDto:
    nombre: str
    valor: float


@dataclass
class MesActualDto:
    total_prima_neta: float
    variacion_mes_anterior: float
    mes_label: str


@dataclass
class CompaniaTopDto:
    nombre: str
    prima_neta: float


@dataclass
class ProduccionDto:
    mes_actual: MesActualDto
    tendencia_12_meses: list[TendenciaMesDto] = field(default_factory=list)
    por_compania: list[ItemValorDto] = field(default_factory=list)
    por_ejecutivo: list[ItemValorDto] = field(default_factory=list)
    por_ramo: list[ItemValorDto] = field(default_factory=list)
    compania_top: CompaniaTopDto | None = None


@dataclass
class ActividadTipoDto:
    tipo: str
    concretadas: int
    pendientes: int


@dataclass
class ResumenActividadesDto:
    agendadas: int
    concretadas: int
    pendientes: int
    porcentaje_cumplimiento: float


@dataclass
class ActividadesComercialesDto:
    por_tipo: list[ActividadTipoDto] = field(default_factory=list)
    resumen: ResumenActividadesDto | None = None


@dataclass
class ItemCantidadDto:
    nombre: str
    cantidad: int


@dataclass
class ReportesPolizasDto:
    por_comuna: list[ItemCantidadDto] = field(default_factory=list)
    por_sexo: list[ItemCantidadDto] = field(default_factory=list)
    por_rango_edad: list[ItemCantidadDto] = field(default_factory=list)
    por_ramo: list[ItemCantidadDto] = field(default_factory=list)


@dataclass
class KpisEvaluacionDto:
    total_proyectos: int
    monto_total_uf: float
    tasa_conversion: float


@dataclass
class EvaluacionProyectosDto:
    kpis: KpisEvaluacionDto | None = None
    por_compania: list[ItemCantidadDto] = field(default_factory=list)
    por_ramo: list[ItemCantidadDto] = field(default_factory=list)


@dataclass
class MetricasDashboardGerenteDto:
    produccion: ProduccionDto | None = None
    actividades_comerciales: ActividadesComercialesDto | None = None
    reportes_polizas: ReportesPolizasDto | None = None
    evaluacion_proyectos: EvaluacionProyectosDto | None = None
