from psycopg.rows import DictRow

from app.dominio.estado_informativo_proceso_comercial.estado_informativo_proceso_comercial import EstadoInformativoProcesoComercial
from app.dominio.etapa_proceso_comercial.etapa_proceso_comercial import EtapaProcesoComercial
from app.dominio.historial_estado.historial_estado import HistorialEstado
from app.dominio.usuario.usuario import Usuario


class DictRowHistorialEstadoAdapter:

    def __init__(self, row: DictRow) -> None:
        self.row = row

    def to_historial_estado(self) -> HistorialEstado:
        etapa = EtapaProcesoComercial(
            codigo=self.row['codigo_etapa'],
            nombre=self.row['etapa'],
            sigiuente_etapa=None,
            dias_limite=None,
            es_terminal=False
        )

        estado = EstadoInformativoProcesoComercial(
            codigo=self.row['codigo_estado'],
            nombre=self.row['estado'],
            etapa=etapa,
            fecha_registro=self.row['fecha_registro']
        )

        usuario = Usuario(
            rut=self.row['rut_registrado_por'],
            nombre=self.row['registrado_por']
        )

        return HistorialEstado(
            estado=estado,
            fecha_registro=self.row['fecha_registro'],
            observacion=self.row['observacion'],
            registrado_por=usuario,
            dias_transcurridos=self.row['dias_transcurridos']
        )