from datetime import datetime

from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.comuna.comuna import Comuna
from app.dominio.estados.estado_particular.estado_particular import EstadoParticular
from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo
from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.usuario.usuario import Usuario

class ProspectoCondominio(Prospecto):
    def __init__(
        self,
        rut_riesgo: str | None, 
        nombre_riesgo: str, 
        telefono_contacto: str, 
        correo_contacto: str | None, 
        direccion: str, 
        comuna: Comuna, 
        estado: EstadoParticular, 
        observaciones: str | None, 
        linea_negocio: LineaNegocio, 
        registrado_por: Usuario, 
        companies_sugeridas: list[CompanySeguros],
        nombre_contacto: str,
        cargo_contacto: str | None, 
        id: int | None = None, 
        evaluacion_riesgo: EvaluacionRiesgo | None = None,
        fecha_registro: datetime | None = None,
        tiene_locales_comerciales: bool | None = None,
        uso_del_condominio: str | None = None,
        numero_pisos: int | None = None,
        numero_torres: int | None = None,
        cantidad_departamentos: int | None = None,
        cantidad_subterraneos: int | None = None,
        tiene_piscina: bool | None = None,
        year_construccion: int | None = None,
        metros_cuadrados: int | None = None,
        desea_ser_contactado: bool | None = None
    ):
        super().__init__(
            id=id,
            rut_riesgo=rut_riesgo,
            nombre_riesgo=nombre_riesgo,
            telefono_contacto=telefono_contacto,
            correo_contacto=correo_contacto,
            direccion=direccion,
            comuna=comuna,
            observaciones=observaciones,
            linea_negocio=linea_negocio,
            registrado_por=registrado_por,
            fecha_registro=fecha_registro,
            companies_sugeridas=companies_sugeridas,
            estado=estado,
            evaluacion_riesgo=evaluacion_riesgo
        )
        
        self.tiene_locales_comerciales = tiene_locales_comerciales
        self.uso_del_condominio = uso_del_condominio
        self.numero_pisos = numero_pisos
        self.numero_torres = numero_torres
        self.cantidad_departamentos = cantidad_departamentos
        self.cantidad_subterraneos = cantidad_subterraneos
        self.tiene_piscina = tiene_piscina
        self.year_construccion = year_construccion
        self.nombre_contacto = nombre_contacto
        self.cargo_contacto = cargo_contacto
        self.metros_cuadrados = metros_cuadrados
        self.desea_ser_contactado = desea_ser_contactado