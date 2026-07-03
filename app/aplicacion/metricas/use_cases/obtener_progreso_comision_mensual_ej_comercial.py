from app.dominio.poliza.repositorio_polizas import RepositorioPolizas
from app.dominio.usuario.usuario import Usuario
from app.infraestructura.lib.uf_api import obtener_valor_uf


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
        comision_uf = 0
        porcentaje_impuesto = 0.2  # 20% de impuesto

        for poliza in polizas:
            comision_uf += poliza.prima_neta * poliza.comision_corredora_pct * ejecutivo_comercial.porcentaje_comision
    
        comision_uf -= comision_uf * porcentaje_impuesto
        valor_uf = obtener_valor_uf()
        return round(comision_uf * valor_uf)