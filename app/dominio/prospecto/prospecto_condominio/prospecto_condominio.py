from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.estados.estado_particular.estado_particular import EstadoParticular
from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo
from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.usuario.usuario import Usuario

class ProspectoCondominio(Prospecto):
    def __init__(
            self, 
            rut_riesgo: str, 
            nombre_riesgo: str, 
            telefono_contacto: str, 
            correo_contacto: str, 
            direccion: str, 
            comuna: str, 
            estado: EstadoParticular, 
            observaciones: str, 
            linea_negocio: LineaNegocio, 
            asistente_comercial: Usuario, 
            companies_sugeridas: list[CompanySeguros],
            nombre_contacto: str,
            cargo_contacto: str, 
            evaluacion_riesgo: EvaluacionRiesgo | None = None,
            tiene_locales_comerciales: bool | None = None,
            uso_del_condominio: str | None = None,
            numero_pisos: int | None = None,
            numero_torres: int | None = None,
            cantidad_departamentos: int | None = None,
            cantidad_subterraneos: int | None = None,
            tiene_piscina: bool | None = None,
            year_construccion: int | None = None
        ):
        super().__init__(rut_riesgo, nombre_riesgo, telefono_contacto, correo_contacto, direccion, comuna, estado, observaciones, linea_negocio, asistente_comercial, companies_sugeridas, evaluacion_riesgo)
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