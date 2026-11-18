from datetime import datetime


class PolizaAlertableRenovacion:
    """Póliza con los datos necesarios para evaluar sus alertas de renovación."""

    def __init__(
        self,
        numero_poliza: str,
        fin_vigencia: datetime,
        id_prospecto: int,
        nombre_cliente: str | None,
        rut_ej_renovacion: str | None,
        rut_as_renovacion: str | None,
        tiene_proceso_renovacion: bool,
        rut_ej_comercial: str | None = None,
    ):
        self.numero_poliza = numero_poliza
        self.fin_vigencia = fin_vigencia
        self.id_prospecto = id_prospecto
        self.nombre_cliente = nombre_cliente
        self.rut_ej_renovacion = rut_ej_renovacion
        self.rut_as_renovacion = rut_as_renovacion
        # Ejecutivo comercial asignado al prospecto del cliente: también es
        # destinatario de las alertas de renovación de sus pólizas.
        self.rut_ej_comercial = rut_ej_comercial
        # True si ya existe un ProcesoComercialRenovacion para la póliza:
        # sus alertas de renovación quedan resueltas y no se generan.
        self.tiene_proceso_renovacion = tiene_proceso_renovacion
