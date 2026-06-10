from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio
from app.infraestructura.administrador_condominio.adaptadores.administrador_condominio_json_adapter import AdministradorCondominioJsonAdapter
from app.infraestructura.linea_negocio.adaptadores.linea_negocio_json_adapter import LineaNegocioJsonAdapter
from app.infraestructura.planificacion_prospecto.adaptadores.planificacion_prospecto_json_adapter import PlanificacionProspectoJsonAdapter
from app.infraestructura.usuario.adaptadores.usuario_json_resumen_adapter import UsuarioJsonResumenAdapter
from app.presentacion.api.prospecto.dto.prospecto_condominio_json import ProspectoCondominioJson


class ProspectoCondominioJsonAdapter:

    def __init__(self, prospecto: ProspectoCondominio):       
        self.prospecto = prospecto

    def to_prospecto_json(self) -> ProspectoCondominioJson:
        if not self.prospecto.id:
            raise Exception('Prospecto inválido, hace falta el id')

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
            self.prospecto.telefono_contacto is not None,
            self.prospecto.correo_contacto is not None,
            self.prospecto.direccion is not None,
            self.prospecto.region is not None,
            self.prospecto.comuna is not None,
            self.prospecto.linea_negocio is not None,
            self.prospecto.tiene_locales_comerciales is not None,
            self.prospecto.uso_del_condominio is not None,
            self.prospecto.materialidad is not None,
            self.prospecto.clasificacion_preliminar_incendio is not None,
            self.prospecto.procesos_productivos is not None,
            self.prospecto.numero_pisos is not None,
            self.prospecto.numero_torres is not None,
            self.prospecto.cantidad_departamentos is not None,
            self.prospecto.cantidad_subterraneos is not None,
            self.prospecto.tiene_piscina is not None,
            self.prospecto.ubicacion_piscina is not None,
            self.prospecto.tiene_alarma_incendio is not None,
            self.prospecto.tiene_sprinklers is not None,
            self.prospecto.year_construccion is not None,
            self.prospecto.metros_cuadrados is not None,
            self.prospecto.uf_por_metro_cuadrado is not None,
            self.prospecto.porcentaje_depreciacion is not None,
            self.prospecto.porcentaje_espacios_comunes is not None,
            datos_completos_planificacion
        ])
        
        return ProspectoCondominioJson(
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
            planificacion_prospecto=PlanificacionProspectoJsonAdapter(self.prospecto.planificacion_prospecto).to_planificacion_prospecto_json() if self.prospecto.planificacion_prospecto else None,
            administrador=AdministradorCondominioJsonAdapter(self.prospecto.administrador).to_json() if self.prospecto.administrador is not None else None,
            uf_por_metro_cuadrado=self.prospecto.uf_por_metro_cuadrado,
            porcentaje_depreciacion=self.prospecto.porcentaje_depreciacion,
            porcentaje_espacios_comunes=self.prospecto.porcentaje_espacios_comunes,
            materialidad=self.prospecto.materialidad,
            clasificacion_preliminar_incendio=self.prospecto.clasificacion_preliminar_incendio,
            procesos_productivos=self.prospecto.procesos_productivos,
            ubicacion_piscina=self.prospecto.ubicacion_piscina,
            tiene_alarma_incendio=self.prospecto.tiene_alarma_incendio,
            tiene_sprinklers=self.prospecto.tiene_sprinklers,
            tiene_locales_comerciales=self.prospecto.tiene_locales_comerciales,
            uso_del_condominio=self.prospecto.uso_del_condominio,
            numero_pisos=self.prospecto.numero_pisos,
            numero_torres=self.prospecto.numero_torres,
            cantidad_departamentos=self.prospecto.cantidad_departamentos,
            cantidad_subterraneos=self.prospecto.cantidad_subterraneos,
            tiene_piscina=self.prospecto.tiene_piscina,
            year_construccion=self.prospecto.year_construccion,
            metros_cuadrados=self.prospecto.metros_cuadrados,
            ultima_actualizacion=self.prospecto.ultima_actualizacion.isoformat(),
            informacion_completa=informacion_completa
        )