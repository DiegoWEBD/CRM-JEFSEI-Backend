from datetime import datetime


from app.dominio.administrador_condominio.administrador_condominio import AdministradorCondominio
from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.planificacion_prospecto.planificacion_prospecto import PlanificacionProspecto
from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.usuario.usuario import Usuario

class ProspectoCondominio(Prospecto):
    def __init__(
        self,
        administrador: AdministradorCondominio | None,
        rut_riesgo: str | None, 
        nombre_riesgo: str | None, 
        telefono_contacto: str | None, 
        correo_contacto: str | None, 
        direccion: str | None, 
        region: str | None,
        comuna: str | None, 
        observaciones: str | None, 
        linea_negocio: LineaNegocio, 
        registrado_por: Usuario, 
        ejecutivo_comercial_asignado: Usuario | None,
        ejecutivo_evaluacion_asignado: Usuario | None,
        uf_por_metro_cuadrado: float | None,
        porcentaje_depreciacion: float | None,
        porcentaje_espacios_comunes: float | None,
        id_cliente: int | None,
        informacion_completa: bool,
        planificacion_prospecto: PlanificacionProspecto | None,
        tiene_locales_comerciales: bool | None,
        uso_del_condominio: str | None,
        materialidad: str | None,
        clasificacion_preliminar_incendio: str | None,
        procesos_productivos: bool | None,
        numero_pisos: int | None,
        numero_torres: int | None,
        cantidad_departamentos: int | None,
        cantidad_subterraneos: int | None,
        tiene_piscina: bool | None,
        ubicacion_piscina: str | None,
        tiene_alarma_incendio: bool | None,
        tiene_sprinklers: bool | None,
        year_construccion: int | None,
        metros_cuadrados: float | None,
        ejecutivo_cobranza_asignado: Usuario | None = None,
        ejecutivo_renovacion_asignado: Usuario | None = None,
        id: int | None = None,
        ultima_actualizacion: datetime = datetime.now(),
    ):
        super().__init__(
            id=id,
            id_cliente=id_cliente,
            rut_riesgo=rut_riesgo,
            nombre_riesgo=nombre_riesgo,
            telefono_contacto=telefono_contacto,
            correo_contacto=correo_contacto,
            direccion=direccion,
            region=region,
            comuna=comuna,
            observaciones=observaciones,
            linea_negocio=linea_negocio,
            registrado_por=registrado_por,
            ejecutivo_comercial_asignado=ejecutivo_comercial_asignado,
            ejecutivo_evaluacion_asignado=ejecutivo_evaluacion_asignado,
            ejecutivo_cobranza_asignado=ejecutivo_cobranza_asignado,
            ejecutivo_renovacion_asignado=ejecutivo_renovacion_asignado,
            planificacion_prospecto=planificacion_prospecto,
            ultima_actualizacion=ultima_actualizacion,
            informacion_completa=informacion_completa
        )
        
        self.tiene_locales_comerciales = tiene_locales_comerciales
        self.uso_del_condominio = uso_del_condominio
        self.numero_pisos = numero_pisos
        self.numero_torres = numero_torres
        self.cantidad_departamentos = cantidad_departamentos
        self.cantidad_subterraneos = cantidad_subterraneos
        self.tiene_piscina = tiene_piscina
        self.year_construccion = year_construccion
        self.metros_cuadrados = metros_cuadrados
        self.uf_por_metro_cuadrado = uf_por_metro_cuadrado
        self.porcentaje_depreciacion = porcentaje_depreciacion
        self.porcentaje_espacios_comunes = porcentaje_espacios_comunes
        self.materialidad = materialidad
        self.administrador = administrador
        self.clasificacion_preliminar_incendio = clasificacion_preliminar_incendio
        self.procesos_productivos = procesos_productivos
        self.ubicacion_piscina = ubicacion_piscina
        self.tiene_alarma_incendio = tiene_alarma_incendio
        self.tiene_sprinklers = tiene_sprinklers