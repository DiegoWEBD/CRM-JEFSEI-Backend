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
        fecha_registro_estado = self.row['fecha_registro_estado']
        codigo_etapa = self.row['codigo_etapa']
        nombre_etapa = self.row['nombre_etapa']
        dias_limite_etapa = self.row['dias_limite_etapa']
        cerrado = self.row['cerrado']
        rut_ej_comercial = self.row['rut_ej_comercial']
        nombre_ej_comercial = self.row['nombre_ej_comercial']
        rut_ej_evaluacion = self.row['rut_ej_evaluacion']
        nombre_ej_evaluacion = self.row['nombre_ej_evaluacion']
        id_producto = self.row['id_producto']
        nombre_producto = self.row['nombre_producto']

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
            nombre=nombre_producto
        )

        etapa = EtapaProcesoComercial(
            codigo=codigo_etapa,
            nombre=nombre_etapa,
            sigiuente_etapa=None,
            dias_limite=dias_limite_etapa
        )

        estado = EstadoInformativoProcesoComercial(
            codigo=codigo_estado,
            etapa=etapa,
            nombre=nombre_estado,
            fecha_registro=fecha_registro_estado
        )

        return ProcesoComercial(
            id=id,
            estado_actual=estado,
            cerrado=cerrado,
            ejecutivo_comercial=ejecutivo_comercial,
            ejecutivo_evaluacion=ejecutivo_evaluacion,
            producto=producto,
            id_prospecto=id_prospecto,
            nombre_cliente=nombre_cliente
        )