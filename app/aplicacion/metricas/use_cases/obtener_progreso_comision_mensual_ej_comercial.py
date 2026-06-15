from app.dominio.poliza.repositorio_polizas import RepositorioPolizas
from app.dominio.usuario.usuario import Usuario


class ObtenerProgresoComisionMensualEjComercialUseCase:
    
    def __init__(
        self, 
        repositorio_polizas: RepositorioPolizas
    ):
        self.repositorio_polizas = repositorio_polizas

    def ejecutar(self, ejecutivo_comercial: Usuario) -> float:
        if ejecutivo_comercial.porcentaje_comision is None:
            raise Exception('El ejecutivo comercial no tiene un porcentaje de comisión asignado')

        polizas = self.repositorio_polizas.polizas_gestionadas_ej_comercial_mes_actual(ejecutivo_comercial.rut)
        comision = 0

        for poliza in polizas:
            comision += poliza.prima_neta * poliza.comision_corredora_pct * ejecutivo_comercial.porcentaje_comision

        return comision