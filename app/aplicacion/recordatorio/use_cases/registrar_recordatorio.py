from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.recordatorio.repositorio_recordatorios import RepositorioRecordatorios


class RegistrarRecordatorioUseCase:

    def __init__(
        self,
        repositorio_recordatorios: RepositorioRecordatorios,
        repositorio_prospectos: RepositorioProspectos,
    ):
        self.repositorio_recordatorios = repositorio_recordatorios
        self.repositorio_prospectos = repositorio_prospectos

    def ejecutar(
        self,
        rut_usuario: str,
        titulo: str,
        detalle: str | None,
        prioridad: str,
        tipo_gestion: str,
        fecha_recordatorio: str,
        id_prospecto: int | None,
    ) -> None:
        if id_prospecto is not None:
            prospecto = self.repositorio_prospectos.buscar(id_prospecto)
            if prospecto is None:
                raise RecursoNoEncontradoException(
                    f'El prospecto con id {id_prospecto} no existe'
                )

        self.repositorio_recordatorios.registrar(
            rut_usuario=rut_usuario,
            titulo=titulo,
            detalle=detalle,
            prioridad=prioridad,
            tipo_gestion=tipo_gestion,
            fecha_recordatorio=fecha_recordatorio,
            id_prospecto=id_prospecto,
        )
