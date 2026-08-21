from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.presentacion.api.proceso_comercial.dto.filtros_procesos_comerciales import FiltrosProcesosComerciales


class ObtenerTodosProcesosComercialesUseCase:

    def __init__(self, repositorio_procesos_comerciales: RepositorioProcesosComerciales):
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales

    def ejecutar(self, filtros: FiltrosProcesosComerciales) -> dict:
        return self.repositorio_procesos_comerciales.obtener_todos(
            texto_busqueda=filtros.texto_busqueda,
            ejecutivos=filtros.ejecutivos,
            etapas=filtros.etapas,
            estado_semaforo=filtros.estado_semaforo,
            estado_proceso=filtros.estado_proceso,
            cerrado=filtros.cerrado,
            fecha_ingreso_etapa_desde=filtros.fecha_desde,
            fecha_ingreso_etapa_hasta=filtros.fecha_hasta,
            pagina=filtros.pagina,
            tamano_pagina=filtros.tamano_pagina,
        )