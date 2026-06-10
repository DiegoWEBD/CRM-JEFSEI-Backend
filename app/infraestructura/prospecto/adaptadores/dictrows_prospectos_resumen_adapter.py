from psycopg.rows import DictRow

from app.aplicacion.proceso_comercial.dto.proceso_comercial_resumen import ProcesoComercialResumen
from app.aplicacion.prospecto.dto.prospecto_resumen import ProspectoResumen


class DictRowsProspectoResumenAdapter:

    def __init__(self, rows: list[DictRow]):
        self.rows = rows

    def to_prospectos_resumen(self) -> list[ProspectoResumen]:
        prospectos: dict[int, ProspectoResumen] = {}

        for row in self.rows:
        
            id = row['id']
            id_proceso_comercial = row['id_proceso_comercial']
            id_cliente = row['id_cliente']
            nombre_riesgo = row['nombre_riesgo']
            nombre_administrador = row['nombre_administrador']
            linea_negocio = row['linea_negocio']
            ejecutivo_comercial = row['ejecutivo_comercial']
            codigo_estado = row['codigo_estado']
            nombre_estado = row['nombre_estado']
            fecha_ultima_accion = row['fecha_ultima_accion']

            if id not in prospectos:
                prospectos[id] = ProspectoResumen(
                    id=id,
                    id_cliente=id_cliente,
                    nombre_riesgo=nombre_riesgo,
                    nombre_administrador=nombre_administrador,
                    linea_negocio=linea_negocio,
                    ejecutivo_comercial=ejecutivo_comercial,
                    procesos_comerciales=[]
                )

            prospectos[id].procesos_comerciales.append(ProcesoComercialResumen(
                id=id_proceso_comercial,
                codigo_estado=codigo_estado,
                nombre_estado=nombre_estado,
                fecha_ultima_accion=fecha_ultima_accion
            ))

        return list(prospectos.values())