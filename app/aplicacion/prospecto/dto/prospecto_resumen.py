from dataclasses import dataclass


@dataclass
class ProspectoResumen:
    id: int
    nombre_riesgo: str
    nombre_contacto: str
    linea_negocio: str
    codigo_estado: str
    nombre_estado: str
    dias_limite: int
    dias_transcurridos: int
    fecha_ultima_accion: str
    proxima_accion: str