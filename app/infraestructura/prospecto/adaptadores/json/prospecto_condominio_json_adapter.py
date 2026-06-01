from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio
from app.infraestructura.evaluacion_riesgo.adaptadores.evaluacion_riesgo_json_adapter import EvaluacionRiesgoJsonAdapter
from app.infraestructura.planificacion_prospecto.adaptadores.planificacion_prospecto_json_adapter import PlanificacionProspectoJsonAdapter
from app.infraestructura.proceso_comercial.adaptadores.proceso_comercial_json_adapter import ProcesoComercialJsonAdapter
from app.infraestructura.usuario.adaptadores.usuario_json_resumen_adapter import UsuarioJsonResumenAdapter
from app.presentacion.api.prospecto.dto.prospecto_condominio_json import ProspectoCondominioJson


class ProspectoCondominioJsonAdapter:

    def __init__(self, prospecto: ProspectoCondominio):

        if not prospecto.id:
            raise Exception('Prospecto inválido, hace falta un id')
        
        self.prospecto = prospecto

    def to_prospecto_json(self) -> ProspectoCondominioJson:

        datos_completos_evaluacion = False

        if self.prospecto.evaluacion_riesgo:
            datos_completos_evaluacion = all([
                self.prospecto.evaluacion_riesgo.uf_por_metro_cuadrado is not None,
                self.prospecto.evaluacion_riesgo.porcentaje_depreciacion is not None,
                self.prospecto.evaluacion_riesgo.porcentaje_espacios_comunes is not None
            ])

        datos_completos_planificacion = True

        if self.prospecto.planificacion_prospecto:
            datos_completos_planificacion = all([
                self.prospecto.planificacion_prospecto.prima_vigente is not None,
                self.prospecto.planificacion_prospecto.company_poliza is not None,
                self.prospecto.planificacion_prospecto.monto_asegurado_vigente is not None
            ])

        informacion_completa = all([
            self.prospecto.rut_riesgo is not None,
            self.prospecto.nombre_riesgo is not None,
            self.prospecto.nombre_contacto is not None,
            self.prospecto.telefono_contacto is not None,
            self.prospecto.correo_contacto is not None,
            self.prospecto.direccion is not None,
            self.prospecto.comuna is not None,
            self.prospecto.cargo_contacto is not None,
            self.prospecto.linea_negocio is not None,
            self.prospecto.proceso_comercial is not None,
            self.prospecto.tiene_locales_comerciales is not None,
            self.prospecto.uso_del_condominio is not None,
            self.prospecto.numero_pisos is not None,
            self.prospecto.numero_torres is not None,
            self.prospecto.cantidad_departamentos is not None,
            self.prospecto.cantidad_subterraneos is not None,
            self.prospecto.tiene_piscina is not None,
            self.prospecto.year_construccion is not None,
            self.prospecto.metros_cuadrados is not None,
            self.prospecto.desea_ser_contactado is not None,
            self.prospecto.cantidad_unidades is not None,
            datos_completos_evaluacion,
            datos_completos_planificacion
        ])
        
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
            companies_sugeridas=[company.nombre for company in self.prospecto.companies_sugeridas],
            evaluacion_riesgo=EvaluacionRiesgoJsonAdapter(self.prospecto.evaluacion_riesgo).to_evaluacion_riesgo_json() if self.prospecto.evaluacion_riesgo else None,
            planificacion_prospecto=PlanificacionProspectoJsonAdapter(self.prospecto.planificacion_prospecto).to_planificacion_prospecto_json() if self.prospecto.planificacion_prospecto else None,
            proceso_comercial=ProcesoComercialJsonAdapter(self.prospecto.proceso_comercial).to_json(),
            tiene_locales_comerciales=self.prospecto.tiene_locales_comerciales,
            uso_del_condominio=self.prospecto.uso_del_condominio,
            numero_pisos=self.prospecto.numero_pisos,
            numero_torres=self.prospecto.numero_torres,
            cantidad_departamentos=self.prospecto.cantidad_departamentos,
            cantidad_subterraneos=self.prospecto.cantidad_subterraneos,
            tiene_piscina=self.prospecto.tiene_piscina,
            year_construccion=self.prospecto.year_construccion,
            metros_cuadrados=self.prospecto.metros_cuadrados,
            desea_ser_contactado=self.prospecto.desea_ser_contactado,
            cantidad_unidades=self.prospecto.cantidad_unidades,
            ultima_actualizacion=self.prospecto.ultima_actualizacion.isoformat(),
            informacion_completa=informacion_completa
        )