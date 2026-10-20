from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.dto.solicitud_cotizacion_request import (
    SolicitudCotizacionRequest,
)
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.unidad_alicuota import UnidadAlicuota
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.validador_alicuotas import (
    validar_unidades,
)


def construir_unidades(request: SolicitudCotizacionRequest) -> list[UnidadAlicuota]:
    """Construye y revalida las unidades importadas antes de persistirlas.

    El navegador nunca es la autoridad sobre los datos aceptados: las reglas
    de negocio se vuelven a comprobar en el servidor.
    """

    unidades = [
        UnidadAlicuota(
            identificador_unidad=unidad.identificador_unidad,
            prorrateo=unidad.prorrateo,
            fila_origen=unidad.fila_origen,
        )
        for unidad in (request.unidades or [])
    ]

    if unidades:
        problemas = validar_unidades(unidades)

        if problemas:
            detalle = '; '.join(
                f'fila {problema.fila_origen}: {problema.mensaje}'
                if problema.fila_origen is not None
                else problema.mensaje
                for problema in problemas[:5]
            )
            raise ConflictoEnAccionException(f'Las unidades importadas no son válidas: {detalle}')

    return unidades
