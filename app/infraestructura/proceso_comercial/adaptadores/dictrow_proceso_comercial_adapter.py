from psycopg.rows import DictRow

from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial
from app.dominio.producto.producto import Producto
from app.dominio.usuario.usuario import Usuario


class DictRowProcesoComercialAdapter:

    def __init__(self, row: DictRow):
        self.row = row

    def to_proceso_comercial(self) -> ProcesoComercial:
        
        id = self.row['id']
        codigo_estado_actual = self.row['codigo_estado_actual']
        cerrado = self.row['cerrado']
        rut_ej_comercial = self.row['rut_ej_comercial']
        nombre_ej_comercial = self.row['nombre_ej_comercial']
        rut_ej_evaluacion = self.row['rut_ej_evaluacion']
        nombre_ej_evaluacion = self.row['nombre_ej_evaluacion']
        id_producto = self.row['id_producto']
        nombre_producto = self.row['nombre_producto']

        ejecutivo_comercial = None
        ejecutivo_evaluacion = None

        if rut_ej_comercial is not None:
            ejecutivo_comercial = Usuario(
                rut=rut_ej_comercial,
                nombre=nombre_ej_comercial
            )

        if rut_ej_evaluacion is not None:
            ejecutivo_evaluacion = Usuario(
                rut=rut_ej_evaluacion,
                nombre=nombre_ej_evaluacion
            )

        producto = Producto(
            id=id_producto,
            nombre=nombre_producto
        )

        return ProcesoComercial(
            id=id,
            historial_estados=[],
            codigo_estado_actual=codigo_estado_actual,
            cerrado=cerrado,
            ejecutivo_comercial=ejecutivo_comercial,
            ejecutivo_evaluacion=ejecutivo_evaluacion,
            producto=producto
        )