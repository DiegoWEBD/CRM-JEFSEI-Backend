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
        color_estado = row['color_estado']
        fecha_ultima_accion = row['fecha_ultima_accion']
        proxima_accion = row['proxima_accion']
        dias_limite_base = row['dias_limite_base']
        dias_limite_particular = row['dias_limite_particular']
        dias_transcurridos = row['dias_transcurridos']

        dias_limite = dias_limite_particular if dias_limite_particular else dias_limite_base

        super().__init__(
            id=id,
            nombre_riesgo=nombre_riesgo,
            nombre_contacto=nombre_contacto,
            linea_negocio=linea_negocio,
            estado=estado,
            color_estado=color_estado,
            fecha_ultima_accion=fecha_ultima_accion,
            proxima_accion=proxima_accion,
            dias_limite=dias_limite,
            dias_transcurridos=dias_transcurridos
        )