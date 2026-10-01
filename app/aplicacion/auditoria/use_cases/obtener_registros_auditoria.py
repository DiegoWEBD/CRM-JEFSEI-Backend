from datetime import datetime

from app.dominio.auditoria.registro_auditoria import RegistroAuditoria
from app.dominio.auditoria.repositorio_auditoria import RepositorioAuditoria


class ObtenerRegistrosAuditoriaUseCase:

    def __init__(self, repositorio_auditoria: RepositorioAuditoria) -> None:
        self.repositorio_auditoria = repositorio_auditoria

    def ejecutar_paginado(
        self,
        categoria: str | None,
        evento: str | None,
        rut_usuario: str | None,
        ip_origen: str | None,
        entidad_tipo: str | None,
        fecha_desde: datetime | None,
        fecha_hasta: datetime | None,
        texto_busqueda: str | None,
        pagina: int,
        tamano_pagina: int,
    ) -> tuple[list[RegistroAuditoria], int]:
        return self.repositorio_auditoria.obtener_paginados(
            categoria=categoria,
            evento=evento,
            rut_usuario=rut_usuario,
            ip_origen=ip_origen,
            entidad_tipo=entidad_tipo,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            texto_busqueda=texto_busqueda,
            pagina=pagina,
            tamano_pagina=tamano_pagina,
        )

    def ejecutar_exportacion(
        self,
        categoria: str | None,
        evento: str | None,
        rut_usuario: str | None,
        ip_origen: str | None,
        entidad_tipo: str | None,
        fecha_desde: datetime | None,
        fecha_hasta: datetime | None,
        texto_busqueda: str | None,
        limite: int = 10000,
    ) -> list[RegistroAuditoria]:
        registros, _ = self.repositorio_auditoria.obtener_paginados(
            categoria=categoria,
            evento=evento,
            rut_usuario=rut_usuario,
            ip_origen=ip_origen,
            entidad_tipo=entidad_tipo,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            texto_busqueda=texto_busqueda,
            pagina=1,
            tamano_pagina=limite,
        )
        return registros
