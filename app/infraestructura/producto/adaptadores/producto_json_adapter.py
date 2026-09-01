from app.dominio.producto.producto import Producto


class ProductoJsonAdapter:

    @staticmethod
    def to_json(producto: Producto) -> dict:
        return {
            'id': producto.id,
            'nombre': producto.nombre,
            'id_linea_negocio': producto.id_linea_negocio,
            'codigo': producto.codigo,
            'eliminado': producto.eliminado,
        }
