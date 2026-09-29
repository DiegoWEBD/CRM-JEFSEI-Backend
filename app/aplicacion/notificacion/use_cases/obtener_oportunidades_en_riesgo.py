from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales


class ObtenerOportunidadesEnRiesgoUseCase:
    """Vista del ejecutivo: sus oportunidades en semáforo amarillo o rojo."""

    def __init__(self, repositorio_procesos: RepositorioProcesosComerciales) -> None:
        self.repositorio_procesos = repositorio_procesos

    def ejecutar_paginado(
        self,
        rut_usuario: str,
        pagina: int,
        tamano_pagina: int,
    ) -> tuple[list, int]:
        return self.repositorio_procesos.obtener_en_riesgo(
            rut_usuario=rut_usuario,
            pagina=pagina,
            tamano_pagina=tamano_pagina,
        )
