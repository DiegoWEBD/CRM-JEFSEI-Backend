class TransicionEstadoProcesoComercial:

    def __init__(
        self,
        codigo_estado_origen: str,
        codigo_estado_destino: str,
        nombre_estado_destino: str,
        es_manual: bool,
        es_principal: bool,
        accion_requerida: str | None,
        nombre_estado_origen: str | None = None,
        dias_limite: int | None = None,
    ):
        self.codigo_estado_origen = codigo_estado_origen
        self.codigo_estado_destino = codigo_estado_destino
        self.nombre_estado_destino = nombre_estado_destino
        self.nombre_estado_origen = nombre_estado_origen
        self.es_manual = es_manual
        self.es_principal = es_principal
        self.accion_requerida = accion_requerida
        # Días límite de permanencia (SLA) del estado de origen.
        # Vive solo en la transición principal (NULL en las secundarias):
        # es el dato que usa el sistema de alertas SLA.
        self.dias_limite = dias_limite
