from datetime import datetime


class ProcesoAlertableSla:
    """Proceso comercial abierto con los datos necesarios para evaluar su SLA."""

    def __init__(
        self,
        id_proceso_comercial: int,
        id_prospecto: int,
        codigo_estado: str,
        nombre_estado: str,
        nombre_etapa: str,
        nombre_prospecto: str | None,
        fecha_ingreso_estado: datetime,
        dias_limite: int | None,
        dias_limite_etapa: int | None,
        rol_responsable: str | None,
        rut_ej_comercial: str | None,
        rut_ej_evaluacion: str | None,
        cerrado: bool,
        codigo_siguiente_estado: str | None = None,
        nombre_siguiente_estado: str | None = None,
        rol_responsable_siguiente: str | None = None,
        accion_requerida: str | None = None,
    ):
        self.id_proceso_comercial = id_proceso_comercial
        self.id_prospecto = id_prospecto
        self.codigo_estado = codigo_estado
        self.nombre_estado = nombre_estado
        self.nombre_etapa = nombre_etapa
        self.nombre_prospecto = nombre_prospecto
        self.fecha_ingreso_estado = fecha_ingreso_estado
        self.dias_limite = dias_limite
        self.dias_limite_etapa = dias_limite_etapa
        self.rol_responsable = rol_responsable
        self.rut_ej_comercial = rut_ej_comercial
        self.rut_ej_evaluacion = rut_ej_evaluacion
        self.cerrado = cerrado
        # Datos del siguiente estado (destino de la transición principal).
        # NULL = sin transición principal -> no genera alertas SLA.
        self.codigo_siguiente_estado = codigo_siguiente_estado
        self.nombre_siguiente_estado = nombre_siguiente_estado
        self.rol_responsable_siguiente = rol_responsable_siguiente
        # Acción que se requiere para completar la transición (texto libre).
        self.accion_requerida = accion_requerida
