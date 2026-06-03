from psycopg.rows import DictRow

from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.producto.producto import Producto


class TupleRowsLineasNegocioAdapter:

    def __init__(self, rows: list[DictRow]):

        if not rows or len(rows) == 0:
            raise ValueError("Lineas de negocio inválidas")
        
        self.rows = rows

    def to_lineas_negocio(self) -> list[LineaNegocio]:
        lineas_negocio: dict[int, LineaNegocio] = {}

        for row in self.rows:
            id_linea_negocio = row['id_linea_negocio']
            linea_negocio = lineas_negocio.get(id_linea_negocio)

            if linea_negocio is None:
                nombre_linea_negocio = row['nombre_linea_negocio']

                linea_negocio = LineaNegocio(
                    id=id_linea_negocio,
                    nombre=nombre_linea_negocio,
                    productos=[]
                )

                lineas_negocio[id_linea_negocio] = linea_negocio
            
            id_producto = row['id_producto']

            if id_producto is not None:
                nombre_producto = row['nombre_producto']

                producto = Producto(
                    id=id_producto,
                    nombre=nombre_producto
                )
                linea_negocio.productos.append(producto)

        return list(lineas_negocio.values())