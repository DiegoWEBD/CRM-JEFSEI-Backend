class TransicionEstadoProcesoComercial:

    def __init__(
        self,
        codigo_estado_origen: str,
        codigo_estado_destino: str,
        nombre_estado_destino: str,
        es_manual: bool,
        es_principal: bool,
        accion_requerida: str | None,
    ):
        self.codigo_estado_origen = codigo_estado_origen
        self.codigo_estado_destino = codigo_estado_destino
        self.nombre_estado_destino = nombre_estado_destino
        self.es_manual = es_manual
        self.es_principal = es_principal
        self.accion_requerida = accion_requerida