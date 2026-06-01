from psycopg.rows import DictRow

from app.dominio.estados.estado_base.estado_base import EstadoBase
from app.dominio.estados.estado_particular.estado_particular import EstadoParticular
from app.dominio.historial_estado.historial_estado import HistorialEstado
from app.dominio.usuario.usuario import Usuario


class DictRowHistorialEstadoAdapter:
    def __init__(self, row: DictRow):
        self.row = row

    def to_historial_estado(self) -> HistorialEstado:
        
        codigo_base_anterior = self.row['codigo_base_anterior']
        nombre_base_anterior = self.row['nombre_base_anterior']
        dias_limite_base_anterior = self.row['dias_limite_base_anterior']
        dias_limite_particular_anterior = self.row['dias_limite_particular_anterior']
        accion_base_anterior = self.row['accion_base_anterior']
        codigo_base_actual = self.row['codigo_base_actual']
        nombre_base_actual = self.row['nombre_base_actual']
        dias_limite_base_actual = self.row['dias_limite_base_actual']
        dias_limite_particular_actual = self.row['dias_limite_particular_actual']
        accion_base_actual = self.row['accion_base_actual']
        codigo_siguiente_estado = self.row['codigo_siguiente_estado']
        nombre_siguiente_estado = self.row['nombre_siguiente_estado']
        dias_limite_siguiente_estado = self.row['dias_limite_siguiente_estado']
        fecha_registro = self.row['fecha_registro']
        motivo_cambio = self.row['motivo_cambio']
        rut_cambiado_por = self.row['rut_cambiado_por']
        nombre_cambiado_por = self.row['nombre_cambiado_por']
        dias_transcurridos = self.row['dias_transcurridos']

        usuario = Usuario(
            rut=rut_cambiado_por,
            nombre=nombre_cambiado_por
        )

        estado_base_anterior = None
        estado_particular_anterior = None
        
        if codigo_base_anterior:
            estado_base_anterior = EstadoBase(
                codigo=codigo_base_anterior,
                nombre=nombre_base_anterior,
                dias_limite=dias_limite_base_anterior,
                accion=accion_base_anterior
            )

            estado_particular_anterior = EstadoParticular(
                estado_base=estado_base_anterior,
                dias_limite_particular=dias_limite_particular_anterior
            )

        estado_base_actual = EstadoBase(
            codigo=codigo_base_actual,
            nombre=nombre_base_actual,
            dias_limite=dias_limite_base_actual,
            accion=accion_base_actual
        )

        estado_base_siguiente = None

        if codigo_siguiente_estado:
            estado_base_siguiente = EstadoBase(
                codigo=codigo_siguiente_estado,
                nombre=nombre_siguiente_estado,
                dias_limite=dias_limite_siguiente_estado
            )

            estado_base_actual.siguiente_estado = estado_base_siguiente

        estado_particular_actual = EstadoParticular(
            estado_base=estado_base_actual,
            dias_limite_particular=dias_limite_particular_actual
        )

        return HistorialEstado(
            estado_anterior=estado_particular_anterior,
            estado_actual=estado_particular_actual,
            fecha_registro=fecha_registro,
            motivo_cambio=motivo_cambio,
            cambiado_por=usuario,
            dias_transcurridos=dias_transcurridos
        )