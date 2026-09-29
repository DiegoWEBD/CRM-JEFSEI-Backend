from psycopg.rows import DictRow

from app.dominio.notificacion.proceso_alertable_sla import ProcesoAlertableSla


class DictRowProcesoAlertableSlaAdapter:

    def __init__(self, row: DictRow):
        self.row = row

    def to_proceso_alertable_sla(self) -> ProcesoAlertableSla:
        r = self.row
        return ProcesoAlertableSla(
            id_proceso_comercial=r['id_proceso_comercial'],
            codigo_estado=r['codigo_estado'],
            nombre_estado=r['nombre_estado'],
            nombre_etapa=r['nombre_etapa'],
            nombre_prospecto=r['nombre_prospecto'],
            fecha_ingreso_estado=r['fecha_ingreso_estado'],
            dias_limite=r['dias_limite'],
            dias_limite_etapa=r['dias_limite_etapa'],
            rol_responsable=r['rol_responsable'],
            rut_ej_comercial=r['rut_ej_comercial'],
            rut_ej_evaluacion=r['rut_ej_evaluacion'],
            cerrado=r['cerrado'],
        )
