from app.dominio.estado_informativo_proceso_comercial.transicion_estado_proceso_comercial import TransicionEstadoProcesoComercial


def crear_transicion_mock(
    codigo_estado_origen: str = "ESTADO_ORIGEN",
    codigo_estado_destino: str = "ESTADO_DESTINO",
    nombre_estado_destino: str = "Estado Destino",
    nombre_estado_origen: str | None = "Estado Origen",
    es_manual: bool = True,
    es_principal: bool = False,
    accion_requerida: str | None = None,
    dias_limite: int | None = None,
) -> TransicionEstadoProcesoComercial:
    return TransicionEstadoProcesoComercial(
        codigo_estado_origen=codigo_estado_origen,
        codigo_estado_destino=codigo_estado_destino,
        nombre_estado_destino=nombre_estado_destino,
        nombre_estado_origen=nombre_estado_origen,
        es_manual=es_manual,
        es_principal=es_principal,
        accion_requerida=accion_requerida,
        dias_limite=dias_limite,
    )
