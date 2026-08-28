from dataclasses import dataclass, field

from app.aplicacion.metricas.dto.kpi_aging_dto import AgingRangoDto


@dataclass
class ConversionConsolidadoDto:
    total_prospectos: int
    prospectos_convertidos: int
    tasa_pct: float


@dataclass
class CierreConsolidadoDto:
    procesos_cerrados: int
    procesos_ganados: int
    procesos_perdidos: int
    tasa_pct: float


@dataclass
class PrimaMetaConsolidadoDto:
    prima_neta_uf: float
    meta_uf: float
    cumplimiento_pct: float


@dataclass
class TiempoCierreConsolidadoDto:
    promedio_dias: float


@dataclass
class AgingConsolidadoDto:
    total_abiertos: int
    rangos: list[AgingRangoDto] = field(default_factory=list)


@dataclass
class RenovacionConsolidadoDto:
    polizas_vencidas: int
    polizas_renovadas: int
    tasa_pct: float


@dataclass
class PrimaRiesgoConsolidadoDto:
    polizas: int
    prima_uf: float


@dataclass
class MorosidadConsolidadoDto:
    total_cuotas: int
    cuotas_morosas: int
    tasa_pct: float


@dataclass
class KpisComercialesDto:
    conversion_prospectos: ConversionConsolidadoDto
    cierre_oportunidades: CierreConsolidadoDto
    prima_vs_meta: PrimaMetaConsolidadoDto
    tiempo_promedio_cierre: TiempoCierreConsolidadoDto
    aging_pipeline: AgingConsolidadoDto
    renovacion: RenovacionConsolidadoDto
    prima_en_riesgo: PrimaRiesgoConsolidadoDto
    morosidad: MorosidadConsolidadoDto
