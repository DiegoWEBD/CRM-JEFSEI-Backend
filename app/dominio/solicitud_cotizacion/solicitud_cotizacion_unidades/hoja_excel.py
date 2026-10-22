class HojaExcel:
    """Hoja disponible dentro de un libro Excel."""

    def __init__(self, nombre: str, filas: int, columnas: int) -> None:
        self.nombre = nombre
        self.filas = filas
        self.columnas = columnas

    def to_dict(self) -> dict:
        return {
            'nombre': self.nombre,
            'filas': self.filas,
            'columnas': self.columnas,
        }
