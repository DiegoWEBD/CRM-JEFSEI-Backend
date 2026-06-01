from pydantic import BaseModel

from app.presentacion.api.evaluacion_riesgo.dto.evaluacion_riesgo_json import EvaluacionRiesgoJson
from app.presentacion.api.planificacion_prospecto.dto.planificacion_prospecto_json import PlanificacionProspectoJson
from app.presentacion.api.proceso_comercial.dto.proceso_comercial_json import ProcesoComercialJson
from app.presentacion.api.usuario.dto.usuario_json_resumen import UsuarioJsonResumen


class ProspectoCondominioJson(BaseModel):
    id: int | None
    rut_riesgo: str | None 
    nombre_riesgo: str 
    nombre_contacto: str
    telefono_contacto: str 
    correo_contacto: str | None 
    direccion: str 
    comuna: str 
    cargo_contacto: str | None
    observaciones: str | None 
    linea_negocio: str 
    registrado_por: UsuarioJsonResumen 
    companies_sugeridas: list[str]
    proceso_comercial: ProcesoComercialJson
    planificacion_prospecto: PlanificacionProspectoJson | None
    evaluacion_riesgo: EvaluacionRiesgoJson | None
    tiene_locales_comerciales: bool | None
    uso_del_condominio: str | None
    numero_pisos: int | None
    numero_torres: int | None
    cantidad_departamentos: int | None
    cantidad_subterraneos: int | None
    tiene_piscina: bool | None
    year_construccion: int | None
    metros_cuadrados: float | None
    desea_ser_contactado: bool | None
    cantidad_unidades: int | None
    ultima_actualizacion: str
    informacion_completa: bool