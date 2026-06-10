class EtapaProcesoComercial:

    def __init__(
        self,
        codigo: str,
        nombre: str,
        sigiuente_etapa: EtapaProcesoComercial | None,
        dias_limite: int | None,
        es_terminal: bool = False
    ):
        self.codigo = codigo
        self.nombre = nombre
        self.siguiente_etapa = sigiuente_etapa
        self.dias_limite = dias_limite
        self.es_terminal = es_terminal