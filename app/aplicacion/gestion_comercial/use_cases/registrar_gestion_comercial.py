from datetime import datetime

from app.dominio.gestion_comercial.gestion_comercial import GestionComercial
from app.dominio.gestion_comercial.repositorio_gestiones_comerciales import RepositorioGestionesComerciales


class RegistrarGestionComercialUseCase:

    def __init__(self, repositorio: RepositorioGestionesComerciales) -> None:
        self.repositorio = repositorio

    def ejecutar(
        self,
        tipo: str,
        rut_usuario: str,
        id_prospecto: int,
        titulo: str,
        estado_contacto: str | None,
        observacion: str | None,
        fecha_gestion: datetime,
    ) -> GestionComercial:
        return self.repositorio.registrar(
            tipo=tipo,
            rut_usuario=rut_usuario,
            id_prospecto=id_prospecto,
            titulo=titulo,
            estado_contacto=estado_contacto,
            observacion=observacion,
            fecha_gestion=fecha_gestion,
        )
