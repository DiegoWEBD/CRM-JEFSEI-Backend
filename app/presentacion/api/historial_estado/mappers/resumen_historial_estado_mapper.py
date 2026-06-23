from app.dominio.historial_estado.historial_estado import HistorialEstado
from app.presentacion.api.historial_estado.dto.historial_estado_resumen import HistorialEstadoResumen
from app.presentacion.api.historial_estado.dto.historial_etapa_resumen import HistorialEtapaResumen


class ResumenHistorialEstadoMapper:
    
    def __init__(self, historial: list[HistorialEstado]) -> None:
        self.historial = historial

    def map(self) -> dict[str, HistorialEtapaResumen]:
        historial_por_etapa: dict[str, HistorialEtapaResumen] = {}

        for item in self.historial:
            etapa = item.estado.etapa
            fecha_registro = item.fecha_registro

            if etapa.nombre not in historial_por_etapa:
                historial_por_etapa[etapa.nombre] = HistorialEtapaResumen(
                    etapa=etapa.nombre,
                    fecha_entrada_etapa=fecha_registro.isoformat(),
                    estados=[]
                )

            historial_por_etapa[etapa.nombre].estados.append(
                HistorialEstadoResumen(
                    estado=item.estado.nombre,
                    observacion=item.observacion,
                    registrado_por=item.registrado_por.nombre,
                    fecha_registro=fecha_registro.isoformat()
                )
            )

        return historial_por_etapa