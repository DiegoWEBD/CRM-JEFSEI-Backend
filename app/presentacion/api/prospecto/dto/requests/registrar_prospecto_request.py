from typing import Optional

from pydantic import BaseModel

from app.presentacion.api.linea_negocio.dto.codigo_linea_negocio import CodigoLineaNegocio


class RegistrarProspectoRequest(BaseModel):
    rut_riesgo: Optional[str] = None
    id_administrador: Optional[int] = None
    nombre_riesgo: str
    telefono_contacto: Optional[str] = None 
    correo_contacto: Optional[str] = None 
    direccion: Optional[str] = None 
    region: Optional[str] = None
    comuna: Optional[str] = None 
    observaciones: Optional[str] = None 
    codigo_linea_negocio: CodigoLineaNegocio
    porcentaje_espacios_comunes: Optional[float] = None
    tiene_locales_comerciales: Optional[bool] = None
    uso_del_condominio: Optional[str] = None
    materialidad: Optional[str] = None
    clasificacion_preliminar_incendio: Optional[str] = None
    procesos_productivos: Optional[bool] = None
    numero_pisos: Optional[int] = None
    numero_torres: Optional[int] = None
    cantidad_departamentos: Optional[int] = None
    cantidad_subterraneos: Optional[int] = None
    tiene_piscina: Optional[bool] = None
    ubicacion_piscina: Optional[str] = None
    tiene_alarma_incendio: Optional[bool] = None
    tiene_sprinklers: Optional[bool] = None
    year_construccion: Optional[int] = None
    metros_cuadrados: Optional[float] = None
    condominio_vertical: Optional[bool] = None
    nombre_fantasia: Optional[str] =  None
    cantidad_trabajadores: Optional[int] =  None
    giros_comerciales: Optional[list[str]] = []
