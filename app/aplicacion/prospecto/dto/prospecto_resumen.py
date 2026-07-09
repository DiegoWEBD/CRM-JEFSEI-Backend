from dataclasses import dataclass

from app.aplicacion.proceso_comercial.dto.proceso_comercial_resumen import ProcesoComercialResumen


@dataclass
class ProspectoResumen:
    id: int
    nombre_riesgo: str
    nombre_administrador: str | None
    linea_negocio: str
    ejecutivo_comercial: str | None
    id_cliente: int | None
    procesos_comerciales: list[ProcesoComercialResumen]
    estado_general_cliente: str