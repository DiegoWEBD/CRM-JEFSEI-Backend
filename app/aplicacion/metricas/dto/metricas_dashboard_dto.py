from dataclasses import dataclass


@dataclass
class TendenciaMesDto:
    mes: str
    prima_neta: float


@dataclass
class ItemValorDto:
    nombre: str
    valor: float


@dataclass
class PrimaNetaMensualDto:
    total_prima_neta: float
    variacion_mes_anterior: float
    mes_label: str


@dataclass
class ComisionMensualDto:
    total_comision: float
    mes_label: str


@dataclass
class CompaniaTopDto:
    nombre: str
    prima_neta: float


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
class ItemCantidadDto:
    nombre: str
    cantidad: int


@dataclass
class PrimaCotizadaDto:
    prima_cotizada: float


@dataclass
class PrimaPotencialEstimadaDto:
    prima_potencial_estimada: float


@dataclass
class PrimaEsperadaDto:
    prima_esperada: float


@dataclass
class ProyeccionPrimaEsperadaDto:
    mes: str
    prima_esperada: float


@dataclass
class TasaCierreDto:
    tasa_cierre_pct: float
    oportunidades_ganadas: int
    oportunidades_cerradas: int
