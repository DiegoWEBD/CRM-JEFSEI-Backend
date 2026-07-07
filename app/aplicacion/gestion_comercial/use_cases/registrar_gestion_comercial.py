from datetime import datetime, timedelta, timezone

from dateutil.relativedelta import relativedelta

from app.dominio.gestion_comercial.gestion_comercial import GestionComercial
from app.dominio.gestion_comercial.repositorio_gestiones_comerciales import RepositorioGestionesComerciales
from app.dominio.recordatorio.repositorio_recordatorios import RepositorioRecordatorios


SCHEDULE_RULES: dict[str, tuple] = {
    'no_contesta':             (timedelta(days=3),  timedelta(days=3),  11),
    'pide_contacto_despues':   (timedelta(days=4),  timedelta(days=4),  8),
    'pendiente de respuesta':  (timedelta(days=3),  timedelta(days=3),  11),
    'no interesado por ahora': (relativedelta(months=2), None,          1),
    'sin respuesta tras seguimiento': (relativedelta(months=2), None,   1),
}


class RegistrarGestionComercialUseCase:

    def __init__(
        self,
        repositorio: RepositorioGestionesComerciales,
        repositorio_recordatorios: RepositorioRecordatorios,
    ) -> None:
        self.repositorio = repositorio
        self.repositorio_recordatorios = repositorio_recordatorios

    def ejecutar(
        self,
        tipo: str,
        rut_usuario: str,
        id_prospecto: int,
        titulo: str,
        estado_contacto: str | None,
        observacion: str | None,
        fecha_gestion: str,
    ) -> GestionComercial:
        gestion = self.repositorio.registrar(
            tipo=tipo,
            rut_usuario=rut_usuario,
            id_prospecto=id_prospecto,
            titulo=titulo,
            estado_contacto=estado_contacto,
            observacion=observacion,
            fecha_gestion=fecha_gestion,
        )

        if tipo == 'llamada' and estado_contacto in SCHEDULE_RULES:
            self._agendar_recordatorios(
                rut_usuario=rut_usuario,
                id_prospecto=id_prospecto,
                titulo=titulo,
                observacion=observacion,
                fecha_gestion=fecha_gestion,
                estado_contacto=estado_contacto,
            )

        return gestion

    def _agendar_recordatorios(
        self,
        rut_usuario: str,
        id_prospecto: int,
        titulo: str,
        observacion: str | None,
        fecha_gestion: str,
        estado_contacto: str,
    ) -> None:
        primer_offset, intervalo, cantidad = SCHEDULE_RULES[estado_contacto]
        base = datetime.fromisoformat(fecha_gestion).replace(tzinfo=timezone.utc)

        for i in range(cantidad):
            offset = primer_offset + (intervalo * i if intervalo is not None else timedelta())
            fecha_recordatorio = (base + offset).isoformat()

            self.repositorio_recordatorios.registrar(
                rut_usuario=rut_usuario,
                titulo=f'Seguimiento: {titulo}',
                detalle=observacion,
                prioridad='alta',
                tipo_gestion='llamada',
                fecha_recordatorio=fecha_recordatorio,
                id_prospecto=id_prospecto,
            )
