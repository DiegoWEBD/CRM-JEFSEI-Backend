from app.aplicacion.prospecto.use_cases.obtener_prospecto_condominio import ObtenerProspectoCondominioUseCase
from app.infraestructura.prospecto.adaptadores.json.prospecto_condominio_json_adapter import ProspectoCondominioJsonAdapter


class ObtenerProspectoFactory:

    def __init__(
        self,
        obtener_prospecto_condominio: ObtenerProspectoCondominioUseCase
    ):

        self.use_cases = {
            'condominio': obtener_prospecto_condominio
        }

        self.adapters = {
            'condominio': ProspectoCondominioJsonAdapter
        }

    def obtener_use_case(self, linea_negocio: str):

        use_case = self.use_cases.get(
            linea_negocio.lower()
        )

        if not use_case:
            raise ValueError(
                f'Línea de negocio {linea_negocio} no soportada'
            )

        return use_case

    def obtener_adapter(self, linea_negocio: str):

        adapter = self.adapters.get(
            linea_negocio.lower()
        )

        if not adapter:
            raise ValueError(
                f'Adapter para línea {linea_negocio} no soportado'
            )

        return adapter

    def obtener(
        self,
        linea_negocio: str,
        id_prospecto: int
    ):

        use_case = self.obtener_use_case(
            linea_negocio
        )

        return use_case.ejecutar(id_prospecto)