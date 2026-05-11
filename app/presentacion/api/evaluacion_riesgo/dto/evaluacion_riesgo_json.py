from pydantic import BaseModel

from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.plan_pago.plan_pago import PlanPago
from app.dominio.poliza.poliza import Poliza
from app.presentacion.api.usuario.dto.usuario_json_resumen import UsuarioJsonResumen


class EvaluacionRiesgoJson(BaseModel):
    id: int
    ej_comercial: UsuarioJsonResumen
    observaciones: str | None
    ej_evaluacion: UsuarioJsonResumen | None