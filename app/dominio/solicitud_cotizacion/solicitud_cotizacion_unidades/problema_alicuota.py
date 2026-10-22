SEVERIDAD_ERROR = 'error'
SEVERIDAD_ADVERTENCIA = 'advertencia'


class ProblemaAlicuota:
    """Problema detectado en una fila importada (o en el conjunto de filas)."""

    def __init__(
        self,
        fila_origen: int | None,
        campo: str | None,
        mensaje: str,
        severidad: str = SEVERIDAD_ERROR,
    ) -> None:
        self.fila_origen = fila_origen
        self.campo = campo
        self.mensaje = mensaje
        self.severidad = severidad

    def to_dict(self) -> dict:
        return {
            'fila_origen': self.fila_origen,
            'campo': self.campo,
            'mensaje': self.mensaje,
            'severidad': self.severidad,
        }
