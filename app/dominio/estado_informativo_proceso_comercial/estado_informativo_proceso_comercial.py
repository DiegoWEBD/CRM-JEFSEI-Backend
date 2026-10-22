from app.dominio.etapa_proceso_comercial.etapa_proceso_comercial import EtapaProcesoComercial


class EstadoInformativoProcesoComercial:

    def __init__(
        self, 
        codigo: str, 
        etapa: EtapaProcesoComercial, 
        nombre: str,
        probabilidad_cierre: float | None = None,
        rol_responsable: str | None = None,
        nombre_rol_responsable: str | None = None,
        cantidad_transiciones: int = 0,
    ):
        self.codigo = codigo
        self.etapa = etapa
        self.nombre = nombre
        self.probabilidad_cierre = probabilidad_cierre
        self.rol_responsable = rol_responsable
        self.nombre_rol_responsable = nombre_rol_responsable
        self.cantidad_transiciones = cantidad_transiciones
