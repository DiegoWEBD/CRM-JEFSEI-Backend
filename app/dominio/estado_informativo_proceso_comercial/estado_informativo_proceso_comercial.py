from app.dominio.etapa_proceso_comercial.etapa_proceso_comercial import EtapaProcesoComercial


class EstadoInformativoProcesoComercial:

    def __init__(self, codigo: str, etapa: EtapaProcesoComercial, nombre: str):
        self.codigo = codigo
        self.etapa = etapa
        self.nombre = nombre