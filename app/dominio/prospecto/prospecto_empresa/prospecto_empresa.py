from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.comuna.comuna import Comuna
from app.dominio.estados.estado_particular.estado_particular import EstadoParticular
from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo
from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.usuario.usuario import Usuario

class ProspectoEmpresa(Prospecto):
    def __init__(
        self,
        rut_riesgo: str | None, 
        nombre_riesgo: str, 
        telefono_contacto: str, 
        correo_contacto: str | None, 
        direccion: str, 
        comuna: Comuna, 
        observaciones: str | None, 
        linea_negocio: LineaNegocio, 
        registrado_por: Usuario, 
        companies_sugeridas: list[CompanySeguros],
        nombre_contacto: str,
        actividad: str,
        ma_rc: float | None,
        ma_edificio: float | None,
        cantidad_trabajadores: int | None,
        estado: EstadoParticular | None = None, 
        id: int | None = None, 
        evaluacion_riesgo: EvaluacionRiesgo | None = None,
    ):
        super().__init__(
            id=id,
            rut_riesgo=rut_riesgo,
            nombre_riesgo=nombre_riesgo,
            nombre_contacto=nombre_contacto,
            telefono_contacto=telefono_contacto,
            correo_contacto=correo_contacto,
            direccion=direccion,
            comuna=comuna,
            observaciones=observaciones,
            linea_negocio=linea_negocio,
            registrado_por=registrado_por,
            companies_sugeridas=companies_sugeridas,
            estado=estado,
            evaluacion_riesgo=evaluacion_riesgo
        )

        self.actividad = actividad
        self.ma_rc = ma_rc
        self.ma_edificio = ma_edificio
        self.cantidad_trabajadores = cantidad_trabajadores
        
        