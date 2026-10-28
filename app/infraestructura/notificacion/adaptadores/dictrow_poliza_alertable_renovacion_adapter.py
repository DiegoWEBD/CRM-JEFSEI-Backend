from psycopg.rows import DictRow

from app.dominio.notificacion.poliza_alertable_renovacion import PolizaAlertableRenovacion


class DictRowPolizaAlertableRenovacionAdapter:

    def __init__(self, row: DictRow):
        self.row = row

    def to_poliza_alertable_renovacion(self) -> PolizaAlertableRenovacion:
        r = self.row
        return PolizaAlertableRenovacion(
            numero_poliza=r['numero_poliza'],
            fin_vigencia=r['fin_vigencia'],
            id_prospecto=r['id_prospecto'],
            nombre_cliente=r['nombre_cliente'],
            rut_ej_renovacion=r['rut_ej_renovacion_asignado'],
            rut_as_renovacion=r['rut_as_renovacion_asignado'],
            tiene_proceso_renovacion=r['tiene_proceso_renovacion'],
        )
