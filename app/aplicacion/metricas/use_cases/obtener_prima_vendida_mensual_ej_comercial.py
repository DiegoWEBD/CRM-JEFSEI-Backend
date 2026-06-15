from app.dominio.poliza.repositorio_polizas import RepositorioPolizas


class ObtenerPrimaVendidaMensualEjComercialUseCase:
    
    def __init__(
        self, 
        repositorio_polizas: RepositorioPolizas
    ):
        self.repositorio_polizas = repositorio_polizas

    def ejecutar(self, rut_ejecutivo: str) -> float:
        polizas = self.repositorio_polizas.polizas_gestionadas_ej_comercial_mes_actual(rut_ejecutivo)
        prima_vendida = 0

        for poliza in polizas:
            prima_vendida += poliza.prima_neta

        return prima_vendida