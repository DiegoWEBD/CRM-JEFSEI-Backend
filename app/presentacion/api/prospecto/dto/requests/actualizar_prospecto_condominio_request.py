from pydantic import BaseModel


class ActualizarProspectoCondominioRequest(BaseModel):
    rut_riesgo: str | None
    nombre_riesgo: str 
    telefono_contacto: str | None
    correo_contacto: str | None 
    direccion: str | None
    region: str | None
    comuna: str | None 
    observaciones: str | None 
    id_linea_negocio: int  
    uf_por_metro_cuadrado: float | None
    porcentaje_depreciacion: float | None
    porcentaje_espacios_comunes: float | None
    tiene_locales_comerciales: bool | None
    uso_del_condominio: str | None
    materialidad: str | None
    clasificacion_preliminar_incendio: str | None
    procesos_productivos: bool | None
    numero_pisos: int | None
    numero_torres: int | None
    cantidad_departamentos: int | None
    cantidad_subterraneos: int | None
    tiene_piscina: bool | None
    ubicacion_piscina: str | None
    tiene_alarma_incendio: bool | None
    tiene_sprinklers: bool | None
    year_construccion: int | None
    metros_cuadrados: float | None