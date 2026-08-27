from app.dominio.poliza.poliza import Poliza
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas


class ObtenerPolizasUseCase:

    def __init__(self, repositorio_polizas: RepositorioPolizas):
        self.repositorio_polizas = repositorio_polizas

    def ejecutar(
        self,
        id_cliente: int | None,
        id_company: int | None,
        id_producto: int | None,
        id_linea_negocio: int | None,
        texto_busqueda: str | None,
        estado: str | None,
        rut_usuario: str | None,
        pagina: int,
        tamano_pagina: int,
    ) -> tuple[list[Poliza], int, dict]:
        return self.repositorio_polizas.obtener_polizas_panel(
            id_cliente=id_cliente,
            id_company=id_company,
            id_producto=id_producto,
            id_linea_negocio=id_linea_negocio,
            texto_busqueda=texto_busqueda,
            estado=estado,
            rut_usuario=rut_usuario,
            pagina=pagina,
            tamano_pagina=tamano_pagina,
        )
