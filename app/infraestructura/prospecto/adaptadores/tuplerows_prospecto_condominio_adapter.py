from psycopg.rows import TupleRow

from app.dominio.comuna.comuna import Comuna
from app.dominio.estados.estado_base.estado_base import EstadoBase
from app.dominio.estados.estado_particular.estado_particular import EstadoParticular
from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio


class TupleRowsProspectoCondominioAdapter(ProspectoCondominio):
    
    def __init__(self, rows: list[TupleRow]):
        id = rows[0]['id_prospecto']
        rut_riesgo = rows[0]['rut_riesgo']
        nombre_riesgo = rows[0]['nombre_riesgo']
        telefono_contacto = rows[0]['telefono_contacto']
        correo_contacto = rows[0]['correo_contacto']
        direccion = rows[0]['direccion']
        nombre_comuna = rows[0]['comuna']
        rut_registrado_por = rows[0]['rut_registrado_por']
        nombre_registrado_por = rows[0]['nombre_registrado_por']
        fecha_registro_prospecto = rows[0]['fecha_registro_prospecto']
        nombre_contacto = rows[0]['nombre_contacto']
        cargo_contacto = rows[0]['cargo_contacto']
        tiene_locales_comerciales = rows[0]['tiene_locales_comerciales']
        uso_del_condominio = rows[0]['uso_del_condominio']
        numero_pisos = rows[0]['numero_pisos']
        numero_torres = rows[0]['numero_torres']
        cantidad_departamentos = rows[0]['cantidad_departamentos']
        cantidad_subterraneos = rows[0]['cantidad_subterraneos']
        tiene_piscina = rows[0]['tiene_piscina']
        year_construccion = rows[0]['year_construccion']
        metros_cuadrados = rows[0]['metros_cuadrados']
        desea_ser_contactado = rows[0]['desea_ser_contactado']
        nombre_estado = rows[0]['nombre_estado']
        codigo_estado = rows[0]['codigo_estado']
        fecha_registro_estado = rows[0]['fecha_registro_estado']
        dias_limite_particular = rows[0]['dias_limite_particular']
        dias_limite_base = rows[0]['dias_limite_base']
        dias_transcurridos = rows[0]['dias_transcurridos']
        observaciones = rows[0]['observaciones']
        nombre_linea_negocio = rows[0]['linea_negocio']

        comuna = Comuna(
            nombre = nombre_comuna
        )

        estado_base  =  EstadoBase(
            codigo = codigo_estado,
            nombre = nombre_estado,
            dias_limite = dias_limite_base
        )

        estado_particular  =  EstadoParticular(
            estado_base = estado_base,
            fecha_resgistro = fecha_registro_estado,
            dias_limite_particular = dias_limite_particular,
            dias_transcurridos = dias_transcurridos
        )

        linea_negocio = LineaNegocio(
            nombre=nombre_linea_negocio
        )

        super().__init__(
            id = id,
            rut_riesgo = rut_riesgo,
            nombre_riesgo = nombre_riesgo,
            telefono_contacto = telefono_contacto,
            correo_contacto = correo_contacto,
            direccion = direccion,
            comuna = comuna,
            estado = estado_particular,
            observaciones = observaciones,
            linea_negocio=linea_negocio,

        )