from psycopg.rows import DictRow

from app.dominio.estado_informativo_proceso_comercial.estado_informativo_proceso_comercial import EstadoInformativoProcesoComercial
from app.dominio.etapa_proceso_comercial.etapa_proceso_comercial import EtapaProcesoComercial
from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial
from app.dominio.producto.producto import Producto
from app.dominio.usuario.usuario import Usuario


class DictRowProcesoComercialAdapter:

    def __init__(self, row: DictRow):
        self.row = row

    def to_proceso_comercial(self) -> ProcesoComercial:
        
        id = self.row['id']
        id_prospecto = self.row['id_prospecto']
        nombre_cliente = self.row['nombre_cliente']
        codigo_estado = self.row['codigo_estado']
        nombre_estado = self.row['nombre_estado']
        codigo_etapa = self.row['codigo_etapa']
        nombre_etapa = self.row['nombre_etapa']
        cerrado = self.row['cerrado']
        rut_ej_comercial = self.row['rut_ej_comercial']
        nombre_ej_comercial = self.row['nombre_ej_comercial']
        rut_ej_evaluacion = self.row['rut_ej_evaluacion']
        nombre_ej_evaluacion = self.row['nombre_ej_evaluacion']
        id_producto = self.row['id_producto']
        codigo_producto = self.row['codigo_producto']
        nombre_producto = self.row['nombre_producto']
        fecha_estimada_cierre = self.row['fecha_estimada_cierre']
        probabilidad_cierre_ejecutivo = self.row['probabilidad_cierre_ejecutivo']
        probabilidad_cierre = self.row['probabilidad_cierre']
        renovacion = self.row['renovacion']
        descartado = self.row['descartado']
        motivo_cierre = self.row['motivo_cierre']
        fecha_cierre = self.row['fecha_cierre']
        fecha_apertura = self.row['fecha_apertura']
        monto_asegurado_actual = self.row['monto_asegurado_actual']
        nombre_excel_alicuota = self.row['nombre_excel_alicuota']

        ejecutivo_comercial = None
        ejecutivo_evaluacion = None

        if rut_ej_comercial is not None:
            ejecutivo_comercial = Usuario(
                rut=rut_ej_comercial,
                nombre=nombre_ej_comercial
            )

        if rut_ej_evaluacion is not None:
            ejecutivo_evaluacion = Usuario(
                rut=rut_ej_evaluacion,
                nombre=nombre_ej_evaluacion
            )

        producto = Producto(
            id=id_producto,
            nombre=nombre_producto,
            codigo=codigo_producto,
            id_linea_negocio=0
        )

        etapa = EtapaProcesoComercial(
            codigo=codigo_etapa,
            nombre=nombre_etapa,
            sigiuente_etapa=None
        )

        estado = EstadoInformativoProcesoComercial(
            codigo=codigo_estado,
            etapa=etapa,
            nombre=nombre_estado,
            probabilidad_cierre=probabilidad_cierre
        )

        return ProcesoComercial(
            id=id,
            estado_actual=estado,
            cerrado=cerrado,
            ejecutivo_comercial=ejecutivo_comercial,
            ejecutivo_evaluacion=ejecutivo_evaluacion,
            producto=producto,
            id_prospecto=id_prospecto,
            nombre_cliente=nombre_cliente,
            fecha_estimada_cierre=fecha_estimada_cierre,
            probabilidad_cierre_ejecutivo=probabilidad_cierre_ejecutivo,
            renovacion=renovacion,
            descartado=descartado,
            motivo_cierre=motivo_cierre,
            fecha_cierre=fecha_cierre,
            fecha_apertura=fecha_apertura,
            monto_asegurado_actual=monto_asegurado_actual,
            nombre_excel_alicuota=nombre_excel_alicuota,
        )