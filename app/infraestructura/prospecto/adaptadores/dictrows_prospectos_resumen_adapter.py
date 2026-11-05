from psycopg.rows import DictRow

from app.aplicacion.proceso_comercial.dto.oportunidades_contadores import OportunidadesContadores
from app.aplicacion.prospecto.dto.prospecto_resumen import ProspectoResumen


class DictRowsProspectoResumenAdapter:

    def __init__(
        self,
        rows: list[DictRow],
        contadores_oportunidades: dict[int, OportunidadesContadores] | None = None,
    ):
        self.rows = rows
        self.contadores_oportunidades = contadores_oportunidades or {}

    def to_prospectos_resumen(self) -> list[ProspectoResumen]:
        prospectos: dict[int, ProspectoResumen] = {}

        for row in self.rows:
        
            id = row['id']
            id_cliente = row['id_cliente']
            rut_riesgo = row['rut_riesgo']
            nombre_riesgo = row['nombre_riesgo']
            nombre_fantasia = row['nombre_fantasia']
            nombre_administrador = row['nombre_administrador']
            linea_negocio = row['linea_negocio']
            ejecutivo_comercial = row['ejecutivo_comercial']
            estado_general_cliente = row['estado_general_cliente']
            comuna = row['comuna']

            if id not in prospectos:
                prospectos[id] = ProspectoResumen(
                    id=id,
                    id_cliente=id_cliente,
                    rut_riesgo=rut_riesgo,
                    nombre_riesgo=nombre_riesgo,
                    nombre_fantasia=nombre_fantasia,
                    nombre_administrador=nombre_administrador,
                    linea_negocio=linea_negocio,
                    ejecutivo_comercial=ejecutivo_comercial,
                    oportunidades=self.contadores_oportunidades.get(
                        id, OportunidadesContadores(comerciales=0, renovaciones=0)
                    ),
                    estado_general_cliente=estado_general_cliente,
                    comuna=comuna
                )

        return list(prospectos.values())
