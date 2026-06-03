from psycopg.rows import DictRow

from app.dominio.comuna.comuna import Comuna
from app.dominio.estados.estado_base.estado_base import EstadoBase
from app.dominio.estados.estado_particular.estado_particular import EstadoParticular
from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo
from app.dominio.historial_estado.historial_estado import HistorialEstado
from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.solicitud_evaluacion_riesgo.solicitud_evaluacion_riesgo import SolicitudEvaluacionRiesgo
from app.dominio.usuario.usuario import Usuario


class TupleRowsProspectoAdapter:
    
    def __init__(self, rows: list[DictRow]):

        if not rows or len(rows) == 0:
            raise Exception("Prospecto inválido")
        
        self.rows = rows

    def to_prospecto(self) -> Prospecto:

        id = self.rows[0]['id_prospecto']
        rut_riesgo = self.rows[0]['rut_riesgo']
        nombre_riesgo = self.rows[0]['nombre_riesgo']
        telefono_contacto = self.rows[0]['telefono_contacto']
        direccion = self.rows[0]['direccion']
        nombre_contacto = self.rows[0]['nombre_contacto']
        correo_contacto = self.rows[0]['correo_contacto']
        observaciones = self.rows[0]['observaciones']
        nombre_linea_negocio = self.rows[0]['linea_negocio']
        rut_registrado_por = self.rows[0]['rut_registrado_por']
        nombre_registrado_por = self.rows[0]['nombre_registrado_por']
        nombre_comuna = self.rows[0]['comuna']  
        updated_at = self.rows[0]['updated_at']

        id_solicitud_evaluacion = self.rows[0]['id_solicitud_evaluacion']
        fecha_solicitud_evaluacion = self.rows[0]['fecha_solicitud_evaluacion']
        prioridad_solicitud = self.rows[0]['prioridad_solicitud']

        id_evaluacion = self.rows[0]['id_evaluacion']
        observaciones_evaluacion = self.rows[0]['observaciones_evaluacion']
        evaluacion_uf_por_metro_cuadrado = self.rows[0]['evaluacion_uf_por_metro_cuadrado']
        evaluacion_porcentaje_depreciacion = self.rows[0]['evaluacion_porcentaje_depreciacion']
        evaluacion_porcentaje_espacios_comunes = self.rows[0]['evaluacion_porcentaje_espacios_comunes']

        rut_ej_comercial = self.rows[0]['rut_ej_comercial']
        nombre_ej_comercial = self.rows[0]['nombre_ej_comercial']
        rut_ej_evaluacion = self.rows[0]['rut_ej_evaluacion']
        nombre_ej_evaluacion = self.rows[0]['nombre_ej_evaluacion']

        comuna = Comuna(
            nombre = nombre_comuna
        )

        linea_negocio = LineaNegocio(
            nombre=nombre_linea_negocio,
            productos=[]
        )

        registrado_por = Usuario(
            rut = rut_registrado_por,
            nombre = nombre_registrado_por
        )

        ej_comercial = None
        ej_evaluacion = None
        solicitud_evaluacion = None
        evaluacion_riesgo = None

        if rut_ej_comercial:
            ej_comercial = Usuario(
                rut = rut_ej_comercial,
                nombre = nombre_ej_comercial
            )

        if rut_ej_evaluacion:
            ej_evaluacion = Usuario(
                rut = rut_ej_evaluacion,
                nombre = nombre_ej_evaluacion
            )

        if id_solicitud_evaluacion:
            solicitud_evaluacion = SolicitudEvaluacionRiesgo(
                id=id_solicitud_evaluacion,
                prioridad=prioridad_solicitud,
                fecha_solicitud=fecha_solicitud_evaluacion
            )

        if id_evaluacion:
            evaluacion_riesgo = EvaluacionRiesgo(
                id = id_evaluacion,
                uf_por_metro_cuadrado=evaluacion_uf_por_metro_cuadrado,
                porcentaje_depreciacion=evaluacion_porcentaje_depreciacion,
                porcentaje_espacios_comunes=evaluacion_porcentaje_espacios_comunes,
                observaciones=observaciones_evaluacion
            )

        historial_estados: list[HistorialEstado] = []

        for row in self.rows:
            nombre_estado_actual = row['nombre_estado_actual']
            codigo_estado_actual = row['codigo_estado_actual']
            color_estado_actual = row['color_estado_actual']
            fecha_registro_estado = row['fecha_registro_estado']
            motivo_cambio_estado = row['motivo_cambio_estado']
            rut_estado_cambiado_por = row['rut_estado_cambiado_por']
            nombre_estado_cambiado_por = row['nombre_estado_cambiado_por']
            dias_limite_particular = row['dias_limite_particular']
            dias_limite_base = row['dias_limite_base']
            codigo_siguiente_estado_esperado = row['codigo_siguiente_estado_esperado']
            nombre_siguiente_estado_esperado = row['nombre_siguiente_estado_esperado']
            proxima_accion_esperada = row['proxima_accion_esperada']
            codigo_estado_anterior = row['codigo_estado_anterior']
            nombre_estado_anterior = row['nombre_estado_anterior']
            dias_transcurridos = row['dias_transcurridos']

            estado_cambiado_por = Usuario(
                rut=rut_estado_cambiado_por,
                nombre=nombre_estado_cambiado_por
            )

            estado_particular_anterior = None

            if codigo_estado_anterior:
                estado_base_anterior = EstadoBase(
                    codigo=codigo_estado_anterior,
                    nombre=nombre_estado_anterior,
                    dias_limite=0 # arbitrario
                )

                estado_particular_anterior = EstadoParticular(
                    estado_base=estado_base_anterior,
                    dias_limite_particular=None
                )

            estado_base_actual = EstadoBase(
                codigo=codigo_estado_actual,
                nombre=nombre_estado_actual,
                dias_limite=dias_limite_base,
                color=color_estado_actual
            )

            siguiente_estado_base_esperado = EstadoBase(
                codigo=codigo_siguiente_estado_esperado,
                nombre=nombre_siguiente_estado_esperado,
                accion=proxima_accion_esperada,
                dias_limite=0 # arbitrario
            )

            estado_base_actual.siguiente_estado = siguiente_estado_base_esperado

            estado_particular_actual = EstadoParticular(
                estado_base=estado_base_actual,
                dias_limite_particular=dias_limite_particular
            )

            historial_estado = HistorialEstado(
                estado_anterior=estado_particular_anterior,
                estado_actual=estado_particular_actual,
                dias_transcurridos=dias_transcurridos,
                fecha_registro=fecha_registro_estado,
                cambiado_por=estado_cambiado_por,
                motivo_cambio=motivo_cambio_estado
            )

            historial_estados.append(historial_estado)


        return Prospecto(
            id = id,
            rut_riesgo = rut_riesgo,
            nombre_riesgo = nombre_riesgo,
            telefono_contacto = telefono_contacto,
            correo_contacto = correo_contacto,
            direccion = direccion,
            comuna = comuna,
            observaciones = observaciones,
            linea_negocio=linea_negocio,
            registrado_por=registrado_por,
            companies_sugeridas=[],
            nombre_contacto=nombre_contacto,
            planificacion_prospecto=None,
            ultima_actualizacion=updated_at
        )