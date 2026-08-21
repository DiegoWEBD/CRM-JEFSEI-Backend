from psycopg.rows import DictRow

from app.presentacion.api.estado_informativo.dto.estado_informativo_json import EstadoInformativoJson
from app.presentacion.api.etapa_proceso_comercial.dto.etapa_proceso_comercial_json import EtapaProcesoComercialJson
from app.presentacion.api.proceso_comercial.dto.estado_semaforo import EstadoSemaforo
from app.presentacion.api.proceso_comercial.dto.proceso_comercial_json import ProcesoComercialJson
from app.presentacion.api.proceso_comercial.dto.reportes_proceso_comercial import ReportesProcesoComercialDTO
from app.presentacion.api.proceso_comercial.dto.reportes_proceso_comercial_cerrado import ReportesProcesoComercialCerradoDTO
from app.presentacion.api.usuario.dto.usuario_json_resumen import UsuarioJsonResumen


class DictRowReporteProcesoComercialAdapter:

    def __init__(self, row: DictRow):
        self.row = row

    def _to_proceso_comercial_json(self) -> ProcesoComercialJson:
        r = self.row
        return ProcesoComercialJson(
            id=r['id'],
            ejecutivo_comercial=UsuarioJsonResumen(
                rut=r['rut_ej_comercial'], nombre=r['nombre_ej_comercial']
            ) if r['rut_ej_comercial'] else None,
            ejecutivo_evaluacion=UsuarioJsonResumen(
                rut=r['rut_ej_evaluacion'], nombre=r['nombre_ej_evaluacion']
            ) if r['rut_ej_evaluacion'] else None,
            id_prospecto=r['id_prospecto'],
            nombre_cliente=r['nombre_cliente'],
            producto=r['nombre_producto'],
            tipo_producto=r['codigo_producto'],
            estado_actual=EstadoInformativoJson(
                codigo=r['codigo_estado'],
                nombre=r['nombre_estado'],
                fecha_registro=r['fecha_registro_estado'].isoformat(),
            ),
            etapa_actual=EtapaProcesoComercialJson(
                codigo=r['codigo_etapa'],
                nombre=r['nombre_etapa'],
                dias_limite=r['dias_limite_etapa'],
            ),
            cerrado=r['cerrado'],
        )

    def to_reporte(self) -> ReportesProcesoComercialDTO | ReportesProcesoComercialCerradoDTO:
        proceso_json = self._to_proceso_comercial_json()

        if not self.row['cerrado']:
            return ReportesProcesoComercialDTO(
                proceso=proceso_json,
                fecha_ingreso_etapa=(
                    self.row['fecha_ingreso_etapa'].isoformat()
                ),
                dias_transcurridos=self.row['dias_transcurridos'],
                porentaje_sla_consumido=float(self.row['porcentaje_sla_consumido']),
                estado_semaforo=EstadoSemaforo(self.row['estado_semaforo']),
                dias_restantes=self.row['dias_restantes'],
                dias_atraso=self.row['dias_atraso'],
                mensaje_semaforo=self.row['mensaje_semaforo'],
            )

        return ReportesProcesoComercialCerradoDTO(
            proceso=proceso_json,
            estado_semaforo=EstadoSemaforo.NO_APLICA,
        )
