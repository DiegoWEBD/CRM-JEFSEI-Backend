from datetime import date, datetime

from app.aplicacion.cobranza.dto.dashboard_cobranza_dto import (
    CuotaDashboardDto,
    DashboardCobranzaDto,
    PolizaSinPlanPagoDto,
)
from app.dominio.cobranza.repositorio_consulta_dashboard_cobranza import (
    RepositorioConsultaDashboardCobranza,
)

DIAS_MORA_MOROSO = 30
DIAS_PROXIMOS = 10


class ObtenerDashboardCobranzaUseCase:

    def __init__(
        self,
        repositorio: RepositorioConsultaDashboardCobranza,
    ):
        self.repositorio = repositorio

    def ejecutar(self, rut_usuario: str) -> DashboardCobranzaDto:
        hoy = date.today()

        cuotas_raw = self.repositorio.obtener_cuotas_dashboard(rut_usuario)
        polizas_sin_plan_raw = self.repositorio.obtener_polizas_sin_plan_pago(rut_usuario)
        recordatorios_raw = self.repositorio.obtener_recordatorios_cobranza(
            rut_usuario, self._sumar_dias(hoy, DIAS_PROXIMOS)
        )

        recordatorio_por_cuota: dict[int, date] = {}
        for r in recordatorios_raw:
            cuota_id = r["cuota_id"]
            fecha_rem = r["fecha_recordatorio"]
            if isinstance(fecha_rem, datetime):
                fecha_rem = fecha_rem.date()
            if cuota_id not in recordatorio_por_cuota or fecha_rem < recordatorio_por_cuota[cuota_id]:
                recordatorio_por_cuota[cuota_id] = fecha_rem

        pagados: list[CuotaDashboardDto] = []
        morosos: list[CuotaDashboardDto] = []
        atrasados: list[CuotaDashboardDto] = []
        llamar_hoy: list[CuotaDashboardDto] = []
        proximos10: list[CuotaDashboardDto] = []

        for row in cuotas_raw:
            cuota = self._row_to_cuota_dashboard(row)
            vencimiento = self._parse_date(row["fecha_vencimiento"])
            pagado = row["pagado"]

            if pagado:
                cuota.estado = "pagado"
                pagados.append(cuota)
                continue

            if vencimiento:
                dias_atraso = (hoy - vencimiento).days
            else:
                dias_atraso = 0

            if dias_atraso > DIAS_MORA_MOROSO:
                cuota.estado = "moroso"
                morosos.append(cuota)
                continue

            if dias_atraso >= 0:
                cuota.estado = "atrasado"
                atrasados.append(cuota)
                continue

            rem_fecha = recordatorio_por_cuota.get(row["cuota_id"])
            if rem_fecha is not None:
                if rem_fecha <= hoy:
                    cuota.estado = "llamarHoy"
                    llamar_hoy.append(cuota)
                    continue
                elif rem_fecha <= self._sumar_dias(hoy, DIAS_PROXIMOS):
                    cuota.estado = "proximos10"
                    proximos10.append(cuota)
                    continue

        sin_plan_pago: list[PolizaSinPlanPagoDto] = []
        for row in polizas_sin_plan_raw:
            sin_plan_pago.append(
                PolizaSinPlanPagoDto(
                    numero_poliza=row["numero_poliza"],
                    id_prospecto=row["id_prospecto"],
                    nombre_cliente=row["nombre_cliente"],
                    producto=row.get("producto", ""),
                    compania=row.get("compania", ""),
                    cancelada=row.get("cancelada", False),
                    telefono_contacto=row.get("telefono_contacto"),
                    rut_riesgo=row.get("rut_riesgo"),
                )
            )

        kpis = {
            "pagados": len(pagados),
            "morosos": len(morosos),
            "atrasados": len(atrasados),
            "sinPlanPago": len(sin_plan_pago),
            "llamarHoy": len(llamar_hoy),
            "proximos10": len(proximos10),
        }

        return DashboardCobranzaDto(
            kpis=kpis,
            pagados=pagados,
            morosos=morosos,
            atrasados=atrasados,
            sin_plan_pago=sin_plan_pago,
            llamar_hoy=llamar_hoy,
            proximos10=proximos10,
        )

    def _row_to_cuota_dashboard(self, row: dict) -> CuotaDashboardDto:
        return CuotaDashboardDto(
            id=row["cuota_id"],
            numero_cuota=row["numero_cuota"],
            fecha_vencimiento=self._fmt_date(row["fecha_vencimiento"]), # type: ignore
            pagado=row["pagado"],
            fecha_pago=self._fmt_date(row.get("fecha_pago")),
            numero_poliza=row.get("numero_poliza", ""),
            nombre_cliente=row.get("nombre_cliente", ""),
            id_prospecto=row.get("id_prospecto", 0),
            producto=row.get("producto", ""),
            total_cuotas=row.get("total_cuotas", 0),
            telefono_contacto=row.get("telefono_contacto"),
            rut_riesgo=row.get("rut_riesgo"),
        )

    def _fmt_date(self, val) -> str | None:
        if val is None:
            return None
        if isinstance(val, (date, datetime)):
            return val.isoformat()
        return str(val)

    def _parse_date(self, val) -> date | None:
        if val is None:
            return None
        if isinstance(val, datetime):
            return val.date()
        if isinstance(val, date):
            return val
        try:
            s = str(val)
            if "T" in s:
                return datetime.fromisoformat(s).date()
            return datetime.strptime(s, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    def _sumar_dias(self, d: date, dias: int) -> date:
        from datetime import timedelta
        return d + timedelta(days=dias)
