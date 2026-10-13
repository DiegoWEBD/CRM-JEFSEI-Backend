from datetime import datetime

from app.dominio.etapa_proceso_comercial.etapa_proceso_comercial import EtapaProcesoComercial


class EstadoInformativoProcesoComercial:

    def __init__(
        self, 
        codigo: str, 
        etapa: EtapaProcesoComercial, 
        nombre: str,
        fecha_registro: datetime | None = None,
        probabilidad_cierre: float | None = None,
        dias_limite: int | None = None,
        rol_responsable: str | None = None,
        nombre_rol_responsable: str | None = None,
        cantidad_transiciones: int = 0,
    ):
        self.codigo = codigo
        self.etapa = etapa
        self.nombre = nombre
        self.fecha_registro = fecha_registro
        self.probabilidad_cierre = probabilidad_cierre
        self.dias_limite = dias_limite
        self.rol_responsable = rol_responsable
        self.nombre_rol_responsable = nombre_rol_responsable
        self.cantidad_transiciones = cantidad_transiciones
