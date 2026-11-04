from datetime import datetime, timezone

from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.planificacion_prospecto.planificacion_prospecto import PlanificacionProspecto
from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.prospecto.prospecto_empresa.giro_comercial import GiroComercial
from app.dominio.usuario.usuario import Usuario


class ProspectoEmpresa(Prospecto):
    def __init__(
        self,
        rut_riesgo: str | None,
        nombre_riesgo: str,
        telefono_contacto: str | None,
        correo_contacto: str | None,
        direccion: str | None,
        region: str | None,
        comuna: str | None,
        observaciones: str | None,
        linea_negocio: LineaNegocio,
        registrado_por: Usuario,
        ejecutivo_comercial_asignado: Usuario | None,
        informacion_completa: bool,
        nombre_fantasia: str | None = None,
        cantidad_trabajadores: int | None = None,
        giros_comerciales: list[GiroComercial] | None = None,
        ejecutivo_evaluacion_asignado: Usuario | None = None,
        ejecutivo_cobranza_asignado: Usuario | None = None,
        ejecutivo_renovacion_asignado: Usuario | None = None,
        asistente_renovacion_asignado: Usuario | None = None,
        ultima_actualizacion: datetime = datetime.now(tz=timezone.utc),
        planificacion_prospecto: PlanificacionProspecto | None = None,
        id: int | None = None,
        id_cliente: int | None = None,
        estado_general_cliente: str | None = None
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
            asistente_renovacion_asignado=asistente_renovacion_asignado,
            planificacion_prospecto=planificacion_prospecto,
            ultima_actualizacion=ultima_actualizacion,
            informacion_completa=informacion_completa,
            estado_general_cliente=estado_general_cliente
        )

        self.nombre_fantasia = nombre_fantasia
        self.cantidad_trabajadores = cantidad_trabajadores
        self.giros_comerciales = giros_comerciales if giros_comerciales is not None else []
