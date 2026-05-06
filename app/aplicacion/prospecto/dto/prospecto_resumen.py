from dataclasses import dataclass


@dataclass
class ProspectoResumen:
    nombre_riesgo: str
    nombre_contacto: str
    linea_negocio: str
    estado: str
    fecha_ultima_accion: str
    proxima_accion: str