from app.dominio.recordatorio.repositorio_recordatorios import RepositorioRecordatorios


class ActualizarRecordatorioUseCase:

    def __init__(self, repositorio_recordatorios: RepositorioRecordatorios):
        self.repositorio_recordatorios = repositorio_recordatorios

    def ejecutar(
        self,
        id: int,
        titulo: str,
        detalle: str | None,
        prioridad: str,
        tipo_gestion: str,
        fecha_recordatorio: str,
        id_prospecto: int | None = None,
    ) -> None:
        self.repositorio_recordatorios.actualizar(
            id=id,
            titulo=titulo,
            detalle=detalle,
            prioridad=prioridad,
            tipo_gestion=tipo_gestion,
            fecha_recordatorio=fecha_recordatorio,
            id_prospecto=id_prospecto,
        )
