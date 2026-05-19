from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio
from app.infraestructura.evaluacion_riesgo.adaptadores.evaluacion_riesgo_json_adapter import EvaluacionRiesgoJsonAdapter
from app.infraestructura.historial_estado.adaptadores.historial_estado_json_adapter import HistorialEstadoJsonAdapter
from app.infraestructura.planificacion_prospecto.adaptadores.planificacion_prospecto_json_adapter import PlanificacionProspectoJsonAdapter
from app.infraestructura.solicitud_evaluacion_riesgo.adaptadores.solicitud_evaluacion_riesgo_json_adapter import SolicitudEvaluacionRiesgoJsonAdapter
from app.infraestructura.usuario.adaptadores.usuario_json_resumen_adapter import UsuarioJsonResumenAdapter
from app.presentacion.api.prospecto.dto.prospecto_condominio_json import ProspectoCondominioJson


class ProspectoCondominioJsonAdapter:

    def __init__(self, prospecto: ProspectoCondominio):

        if not prospecto.id:
            raise Exception('Prospecto inválido, hace falta un id')
        
        self.prospecto = prospecto

    def to_prospecto_json(self) -> ProspectoCondominioJson:
        
        return ProspectoCondominioJson(
            id=self.prospecto.id,
            rut_riesgo=self.prospecto.rut_riesgo,
            nombre_riesgo=self.prospecto.nombre_riesgo,
            nombre_contacto=self.prospecto.nombre_contacto,
            telefono_contacto=self.prospecto.telefono_contacto,
            correo_contacto=self.prospecto.correo_contacto,
            direccion=self.prospecto.direccion,
            comuna=self.prospecto.comuna.nombre,
            cargo_contacto=self.prospecto.cargo_contacto,
            observaciones=self.prospecto.observaciones,
            linea_negocio=self.prospecto.linea_negocio.nombre,
            registrado_por=UsuarioJsonResumenAdapter(self.prospecto.registrado_por).to_usuario_json_resumen(),
            ejecutivo_comercial=UsuarioJsonResumenAdapter(self.prospecto.ejecutivo_comercial_asignado).to_usuario_json_resumen() if self.prospecto.ejecutivo_comercial_asignado else None,
            ejecutivo_evaluacion=UsuarioJsonResumenAdapter(self.prospecto.ejecutivo_evaluacion_asignado).to_usuario_json_resumen() if self.prospecto.ejecutivo_evaluacion_asignado else None,
            companies_sugeridas=[company.nombre for company in self.prospecto.companies_sugeridas],
            historial_estados=[HistorialEstadoJsonAdapter(historial).to_historial_estado_json() for historial in self.prospecto.historial_estados],
            solicitud_evaluacion_riesgo=SolicitudEvaluacionRiesgoJsonAdapter(self.prospecto.solicitud_evaluacion_riesgo).to_solicitud_evaluacion_riesgo_json() if self.prospecto.solicitud_evaluacion_riesgo else None,
            evaluacion_riesgo=EvaluacionRiesgoJsonAdapter(self.prospecto.evaluacion_riesgo).to_evaluacion_riesgo_json() if self.prospecto.evaluacion_riesgo else None,
            planificacion_prospecto=PlanificacionProspectoJsonAdapter(self.prospecto.planificacion_prospecto).to_planificacion_prospecto_json() if self.prospecto.planificacion_prospecto else None,
            tiene_locales_comerciales=self.prospecto.tiene_locales_comerciales,
            uso_del_condominio=self.prospecto.uso_del_condominio,
            numero_pisos=self.prospecto.numero_pisos,
            numero_torres=self.prospecto.numero_torres,
            cantidad_departamentos=self.prospecto.cantidad_departamentos,
            cantidad_subterraneos=self.prospecto.cantidad_subterraneos,
            tiene_piscina=self.prospecto.tiene_piscina,
            year_construccion=self.prospecto.year_construccion,
            metros_cuadrados=self.prospecto.metros_cuadrados,
            desea_ser_contactado=self.prospecto.desea_ser_contactado
        )