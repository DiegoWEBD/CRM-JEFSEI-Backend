from app.dominio.prospecto.prospecto_empresa.prospecto_empresa import ProspectoEmpresa
from app.infraestructura.linea_negocio.adaptadores.linea_negocio_json_adapter import LineaNegocioJsonAdapter
from app.infraestructura.planificacion_prospecto.adaptadores.planificacion_prospecto_json_adapter import PlanificacionProspectoJsonAdapter
from app.infraestructura.usuario.adaptadores.usuario_json_resumen_adapter import UsuarioJsonResumenAdapter
from app.presentacion.api.prospecto.dto.prospecto_empresa_json import ProspectoEmpresaJson


class ProspectoEmpresaJsonAdapter:

    def __init__(self, prospecto: ProspectoEmpresa):
        self.prospecto = prospecto

    def to_prospecto_json(self) -> ProspectoEmpresaJson:
        if not self.prospecto.id:
            raise Exception('Prospecto inválido, hace falta el id')

        return ProspectoEmpresaJson(
            id=self.prospecto.id,
            id_cliente=self.prospecto.id_cliente,
            rut_riesgo=self.prospecto.rut_riesgo,
            nombre_riesgo=self.prospecto.nombre_riesgo,
            telefono_contacto=self.prospecto.telefono_contacto,
            correo_contacto=self.prospecto.correo_contacto,
            direccion=self.prospecto.direccion,
            region=self.prospecto.region,
            comuna=self.prospecto.comuna,
            observaciones=self.prospecto.observaciones,
            linea_negocio=LineaNegocioJsonAdapter(self.prospecto.linea_negocio).to_json(),
            registrado_por=UsuarioJsonResumenAdapter(self.prospecto.registrado_por).to_usuario_json_resumen(),
            ejecutivo_comercial_asignado=UsuarioJsonResumenAdapter(self.prospecto.ejecutivo_comercial_asignado).to_usuario_json_resumen() if self.prospecto.ejecutivo_comercial_asignado else None,
            ejecutivo_evaluacion_asignado=UsuarioJsonResumenAdapter(self.prospecto.ejecutivo_evaluacion_asignado).to_usuario_json_resumen() if self.prospecto.ejecutivo_evaluacion_asignado else None,
            ejecutivo_cobranza_asignado=UsuarioJsonResumenAdapter(self.prospecto.ejecutivo_cobranza_asignado).to_usuario_json_resumen() if self.prospecto.ejecutivo_cobranza_asignado else None,
            ejecutivo_renovacion_asignado=UsuarioJsonResumenAdapter(self.prospecto.ejecutivo_renovacion_asignado).to_usuario_json_resumen() if self.prospecto.ejecutivo_renovacion_asignado else None,
            planificacion_prospecto=PlanificacionProspectoJsonAdapter(self.prospecto.planificacion_prospecto).to_planificacion_prospecto_json() if self.prospecto.planificacion_prospecto else None,
            nombre_fantasia=self.prospecto.nombre_fantasia,
            cantidad_trabajadores=self.prospecto.cantidad_trabajadores,
            giros_comerciales=[giro.nombre for giro in self.prospecto.giros_comerciales],
            ultima_actualizacion=self.prospecto.ultima_actualizacion.isoformat(),
            informacion_completa=self.prospecto.informacion_completa,
            estado_general_cliente=self.prospecto.estado_general_cliente or 'prospecto'
        )
