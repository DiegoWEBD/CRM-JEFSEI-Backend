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
                etapa=EtapaProcesoComercialJson(
                    codigo=r['codigo_etapa'],
                    nombre=r['nombre_etapa'],
                ),
            ),
            etapa_actual=EtapaProcesoComercialJson(
                codigo=r['codigo_etapa'],
                nombre=r['nombre_etapa'],
            ),
            cerrado=r['cerrado'],
            descartado=r['descartado'],
            renovacion=r['renovacion'],
        )

    def to_reporte(self) -> ReportesProcesoComercialDTO | ReportesProcesoComercialCerradoDTO:
        proceso_json = self._to_proceso_comercial_json()

        if not self.row['cerrado']:
            fecha_ingreso = self.row['fecha_ingreso_estado']
            porcentaje = self.row['porcentaje_sla_consumido']
            dias_transcurridos = self.row['dias_transcurridos']
            dias_restantes = self.row['dias_restantes']
            dias_atraso = self.row['dias_atraso']

            return ReportesProcesoComercialDTO(
                proceso=proceso_json,
                fecha_ingreso_estado=(
                    fecha_ingreso.isoformat() if fecha_ingreso else None
                ),
                # Días decimales: se conserva la fracción para mostrar horas.
                dias_transcurridos=(
                    float(dias_transcurridos) if dias_transcurridos is not None else None
                ),
                porentaje_sla_consumido=(
                    float(porcentaje) if porcentaje is not None else None
                ),
                estado_semaforo=EstadoSemaforo(self.row['estado_semaforo']),
                dias_limite=self.row['dias_limite_transicion'],
                dias_restantes=(
                    float(dias_restantes) if dias_restantes is not None else None
                ),
                dias_atraso=(float(dias_atraso) if dias_atraso is not None else None),
                mensaje_semaforo=self.row['mensaje_semaforo'],
            )

        return ReportesProcesoComercialCerradoDTO(
            proceso=proceso_json,
            estado_semaforo=EstadoSemaforo.NO_APLICA,
        )
