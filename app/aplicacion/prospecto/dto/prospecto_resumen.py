from dataclasses import dataclass

from app.aplicacion.proceso_comercial.dto.oportunidades_contadores import OportunidadesContadores


@dataclass
class ProspectoResumen:
    id: int
    rut_riesgo: str
    nombre_riesgo: str
    nombre_fantasia: str | None
    nombre_administrador: str | None
    linea_negocio: str
    ejecutivo_comercial: str | None
    id_cliente: int | None
    oportunidades: OportunidadesContadores
    estado_general_cliente: str
    comuna: str