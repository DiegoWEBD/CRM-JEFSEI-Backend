from psycopg.rows import TupleRow

from app.dominio.comuna.comuna import Comuna
from app.dominio.estados.estado_base.estado_base import EstadoBase
from app.dominio.estados.estado_particular.estado_particular import EstadoParticular
from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo
from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio
from app.dominio.usuario.usuario import Usuario


class TupleRowsProspectoCondominioAdapter(ProspectoCondominio):
    
    def __init__(self, rows: list[TupleRow]):

        if not rows or len(rows) == 0:
            raise Exception("Prospecto inválido")
        
        self.rows = rows

    def to_prospecto_condominio(self) -> ProspectoCondominio:

        id = self.rows[0]['id_prospecto']
        rut_riesgo = self.rows[0]['rut_riesgo']
        nombre_riesgo = self.rows[0]['nombre_riesgo']
        telefono_contacto = self.rows[0]['telefono_contacto']
        correo_contacto = self.rows[0]['correo_contacto']
        direccion = self.rows[0]['direccion']
        nombre_comuna = self.rows[0]['comuna']
        rut_registrado_por = self.rows[0]['rut_registrado_por']
        nombre_registrado_por = self.rows[0]['nombre_registrado_por']
        nombre_contacto = self.rows[0]['nombre_contacto']
        cargo_contacto = self.rows[0]['cargo_contacto']
        tiene_locales_comerciales = self.rows[0]['tiene_locales_comerciales']
        uso_del_condominio = self.rows[0]['uso_del_condominio']
        numero_pisos = self.rows[0]['numero_pisos']
        numero_torres = self.rows[0]['numero_torres']
        cantidad_departamentos = self.rows[0]['cantidad_departamentos']
        cantidad_subterraneos = self.rows[0]['cantidad_subterraneos']
        tiene_piscina = self.rows[0]['tiene_piscina']
        year_construccion = self.rows[0]['year_construccion']
        metros_cuadrados = self.rows[0]['metros_cuadrados']
        desea_ser_contactado = self.rows[0]['desea_ser_contactado']
        observaciones = self.rows[0]['observaciones']
        nombre_linea_negocio = self.rows[0]['linea_negocio']
        id_evaluacion = self.rows[0]['id_evaluacion']
        rut_ej_comercial = self.rows[0]['rut_ej_comercial']
        nombre_ej_comercial = self.rows[0]['nombre_ej_comercial']
        rut_ej_evaluacion = self.rows[0]['rut_ej_evaluacion']
        nombre_ej_evaluacion = self.rows[0]['nombre_ej_evaluacion']
        observaciones_evaluacion = self.rows[0]['observaciones_evaluacion']

        comuna = Comuna(
            nombre = nombre_comuna
        )

        linea_negocio = LineaNegocio(
            nombre=nombre_linea_negocio,
            productos=[]
        )

        registrado_por = Usuario(
            rut = rut_registrado_por,
            nombre = nombre_registrado_por,
            correo='',
            telefono=''
        )

        evaluacion_riesgo = None

        if id_evaluacion is not None:

            ej_comercial = Usuario(
                rut = rut_ej_comercial,
                nombre = nombre_ej_comercial,
                correo='',
                telefono=''
            )

            ej_evaluacion = None

            if rut_ej_evaluacion is not None:
                ej_evaluacion = Usuario(
                    rut = rut_ej_evaluacion,
                    nombre = nombre_ej_evaluacion,
                    correo='',
                    telefono=''
                )

            evaluacion_riesgo = EvaluacionRiesgo(
                id = id_evaluacion,
                cotizaciones = [],
                ej_comercial = ej_comercial,
                observaciones = observaciones_evaluacion,
                ej_evaluacion = ej_evaluacion
            )

        historial_estados: list[EstadoParticular] = []

        for row in self.rows:
            nombre_estado = row['nombre_estado']
            codigo_estado = row['codigo_estado']
            fecha_registro_estado = row['fecha_registro_estado']
            dias_limite_particular = row['dias_limite_particular']
            dias_limite_base = row['dias_limite_base']
            codigo_siguiente_estado = row['codigo_siguiente_estado']
            nombre_siguiente_estado = row['nombre_siguiente_estado']
            dias_transcurridos = row['dias_transcurridos']

            siguiente_estado = None

            if codigo_siguiente_estado is not None:
                siguiente_estado = EstadoBase(
                    codigo = codigo_siguiente_estado,
                    nombre = nombre_siguiente_estado,
                    dias_limite = dias_limite_base
                )

            estado_base  =  EstadoBase(
                codigo = codigo_estado,
                nombre = nombre_estado,
                dias_limite = dias_limite_base,
                siguiente_estado = siguiente_estado,
            )

            estado_particular  =  EstadoParticular(
                estado_base = estado_base,
                fecha_resgistro = fecha_registro_estado,
                dias_limite_particular = dias_limite_particular,
                dias_transcurridos = dias_transcurridos
            )

            historial_estados.append(estado_particular)

        return ProspectoCondominio(
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
            cargo_contacto=cargo_contacto,
            historial_estados=historial_estados,
            evaluacion_riesgo=evaluacion_riesgo,
            tiene_locales_comerciales=tiene_locales_comerciales,
            uso_del_condominio=uso_del_condominio,
            numero_pisos=numero_pisos,
            numero_torres=numero_torres,
            cantidad_departamentos=cantidad_departamentos,
            cantidad_subterraneos=cantidad_subterraneos,
            tiene_piscina=tiene_piscina,
            year_construccion=year_construccion,
            metros_cuadrados=metros_cuadrados,
            desea_ser_contactado=desea_ser_contactado
        )