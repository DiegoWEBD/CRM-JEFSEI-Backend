from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.comuna.comuna import Comuna
from app.dominio.estados.estado_particular.estado_particular import EstadoParticular
from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo
from app.dominio.historial_estado.historial_estado import HistorialEstado
from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.planificacion_prospecto.planificacion_prospecto import PlanificacionProspecto
from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.solicitud_evaluacion_riesgo.solicitud_evaluacion_riesgo import SolicitudEvaluacionRiesgo
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
        historial_estados: list[HistorialEstado], 
        observaciones: str | None, 
        linea_negocio: LineaNegocio, 
        registrado_por: Usuario, 
        ejecutivo_comercial_asignado: Usuario | None,
        ejecutivo_evaluacion_asignado: Usuario | None,
        companies_sugeridas: list[CompanySeguros],
        nombre_contacto: str,
        actividad: str,
        ma_rc: float | None,
        ma_edificio: float | None,
        cantidad_trabajadores: int | None,
        id: int | None = None, 
        evaluacion_riesgo: EvaluacionRiesgo | None = None,
        planificacion_prospecto: PlanificacionProspecto | None = None,
        solicitud_evaluacion_riesgo: SolicitudEvaluacionRiesgo | None = None
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
            evaluacion_riesgo=evaluacion_riesgo,
            historial_estados=historial_estados,
            planificacion_prospecto=planificacion_prospecto,
            solicitud_evaluacion_riesgo=solicitud_evaluacion_riesgo,
            ejecutivo_comercial_asignado=ejecutivo_comercial_asignado,
            ejecutivo_evaluacion_asignado=ejecutivo_evaluacion_asignado
        )

        self.actividad = actividad
        self.ma_rc = ma_rc
        self.ma_edificio = ma_edificio
        self.cantidad_trabajadores = cantidad_trabajadores
        
        