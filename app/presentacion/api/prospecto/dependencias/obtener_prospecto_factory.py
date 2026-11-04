from app.aplicacion.prospecto.use_cases.obtener_prospecto_condominio import ObtenerProspectoCondominioUseCase
from app.aplicacion.prospecto.use_cases.obtener_prospecto_lineas_comerciales import ObtenerProspectoLineasComercialesUseCase
from app.aplicacion.prospecto.use_cases.obtener_prospecto_lineas_personales import ObtenerProspectoLineasPersonalesUseCase
from app.dominio.linea_negocio.linea_negocio import (
    CODIGO_LINEA_CONDOMINIOS,
    CODIGO_LINEAS_COMERCIALES,
    CODIGO_LINEAS_PERSONALES,
)
from app.infraestructura.prospecto.adaptadores.json.prospecto_condominio_json_adapter import ProspectoCondominioJsonAdapter
from app.infraestructura.prospecto.adaptadores.json.prospecto_empresa_json_adapter import ProspectoEmpresaJsonAdapter
from app.infraestructura.prospecto.adaptadores.json.prospecto_json_adapter import ProspectoJsonAdapter


class ObtenerProspectoFactory:

    def __init__(
        self,
        obtener_prospecto_condominio: ObtenerProspectoCondominioUseCase,
        obtener_prospecto_linea_personal: ObtenerProspectoLineasPersonalesUseCase,
        obtener_prospecto_linea_comercial: ObtenerProspectoLineasComercialesUseCase
    ):

        self.use_cases = {
            CODIGO_LINEA_CONDOMINIOS: obtener_prospecto_condominio,
            CODIGO_LINEAS_PERSONALES: obtener_prospecto_linea_personal,
            CODIGO_LINEAS_COMERCIALES: obtener_prospecto_linea_comercial
        }

        self.adapters = {
            CODIGO_LINEA_CONDOMINIOS: ProspectoCondominioJsonAdapter,
            CODIGO_LINEAS_PERSONALES: ProspectoJsonAdapter,
            CODIGO_LINEAS_COMERCIALES: ProspectoEmpresaJsonAdapter
        }

    def obtener_use_case(self, codigo_linea_negocio: str):

        use_case = self.use_cases.get(
            codigo_linea_negocio.lower()
        )

        if not use_case:
            raise ValueError(
                f'Línea de negocio {codigo_linea_negocio} no soportada'
            )

        return use_case

    def obtener_adapter(self, codigo_linea_negocio: str):

        adapter = self.adapters.get(
            codigo_linea_negocio.lower()
        )

        if not adapter:
            raise ValueError(
                f'Adapter para línea {codigo_linea_negocio} no soportado'
            )

        return adapter

    def obtener(
        self,
        codigo_linea_negocio: str,
        id_prospecto: int,
        rut_usuario: str | None
    ):

        use_case = self.obtener_use_case(
            codigo_linea_negocio
        )

        return use_case.ejecutar(id_prospecto, rut_usuario)
