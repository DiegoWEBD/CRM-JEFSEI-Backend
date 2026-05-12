from psycopg.rows import TupleRow

from app.aplicacion.prospecto.dto.prospecto_resumen import ProspectoResumen


class TupleRowProspectoResumenAdapter(ProspectoResumen):

    def __init__(self, row: TupleRow):
        
        if row is None:
            raise Exception('Prospecto inválido')

        id = row['id']
        nombre_riesgo = row['nombre_riesgo']
        nombre_contacto = row['nombre_contacto']
        linea_negocio = row['linea_negocio']
        estado = row['estado']
        fecha_ultima_accion = row['fecha_ultima_accion']
        proxima_accion = row['proxima_accion']

        super().__init__(
            id=id,
            nombre_riesgo=nombre_riesgo,
            nombre_contacto=nombre_contacto,
            linea_negocio=linea_negocio,
            estado=estado,
            fecha_ultima_accion=fecha_ultima_accion,
            proxima_accion=proxima_accion
        )