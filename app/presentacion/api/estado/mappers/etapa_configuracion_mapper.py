from app.dominio.estado_informativo_proceso_comercial.estado_informativo_proceso_comercial import EstadoInformativoProcesoComercial
from app.presentacion.api.estado.dto.etapa_configuracion_json import EtapaConfiguracionJson
from app.presentacion.api.estado.mappers.estado_configuracion_mapper import EstadoConfiguracionMapper


class EtapaConfiguracionMapper:
    """Agrupa los estados por etapa preservando el orden en que llegan.

    El repositorio ya devuelve la lista ordenada por etapa y, dentro de cada
    una, por probabilidad de cierre ascendente; aquí solo se agrupa para no
    perder ese orden.
    """

    def __init__(self, estados: list[EstadoInformativoProcesoComercial]) -> None:
        self.estados = estados

    def map(self) -> list[EtapaConfiguracionJson]:
        etapas: list[EtapaConfiguracionJson] = []
        indices: dict[str, int] = {}

        for estado in self.estados:
            codigo_etapa = estado.etapa.codigo
            indice = indices.get(codigo_etapa)

            if indice is None:
                indice = len(etapas)
                indices[codigo_etapa] = indice
                etapas.append(
                    EtapaConfiguracionJson(
                        codigo_etapa=codigo_etapa,
                        nombre_etapa=estado.etapa.nombre,
                        dias_limite_etapa=estado.etapa.dias_limite,
                        estados=[],
                    )
                )

            etapas[indice].estados.append(
                EstadoConfiguracionMapper.map_one(estado)
            )

        return etapas
