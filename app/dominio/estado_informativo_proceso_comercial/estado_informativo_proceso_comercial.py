from app.dominio.etapa_proceso_comercial.etapa_proceso_comercial import EtapaProcesoComercial


class EstadoInformativoProcesoComercial:

    def __init__(
        self, 
        codigo: str, 
        nombre: str,
        etapa: EtapaProcesoComercial = EtapaProcesoComercial(codigo='', nombre='', sigiuente_etapa=None), 
        probabilidad_cierre: float | None = None,
        cantidad_transiciones: int = 0,
    ):
        self.codigo = codigo
        self.etapa = etapa
        self.nombre = nombre
        self.probabilidad_cierre = probabilidad_cierre
        self.cantidad_transiciones = cantidad_transiciones
