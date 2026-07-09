from dataclasses import dataclass, field


@dataclass
class CuotaDashboardDto:
    id: int
    numero_cuota: int
    fecha_vencimiento: str
    pagado: bool
    fecha_pago: str | None = None
    numero_poliza: str = ""
    nombre_cliente: str = ""
    id_prospecto: int = 0
    estado: str = ""
    producto: str = ""
    total_cuotas: int = 0
    telefono_contacto: str | None = None
    rut_riesgo: str | None = None


@dataclass
class PolizaSinPlanPagoDto:
    numero_poliza: str
    id_prospecto: int
    nombre_cliente: str
    producto: str
    compania: str
    cancelada: bool = False
    telefono_contacto: str | None = None
    rut_riesgo: str | None = None


@dataclass
class DashboardCobranzaDto:
    kpis: dict[str, int]
    pagados: list[CuotaDashboardDto] = field(default_factory=list)
    morosos: list[CuotaDashboardDto] = field(default_factory=list)
    atrasados: list[CuotaDashboardDto] = field(default_factory=list)
    sin_plan_pago: list[PolizaSinPlanPagoDto] = field(default_factory=list)
    llamar_hoy: list[CuotaDashboardDto] = field(default_factory=list)
    proximos10: list[CuotaDashboardDto] = field(default_factory=list)
