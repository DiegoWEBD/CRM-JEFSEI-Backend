from app.dominio.cliente.cliente import Cliente
from app.dominio.evaluacion_riesgo.evaluacion_riesgo import EvaluacionRiesgo

class Poliza:
    def __init__(self, numero_poliza: str, cliente: Cliente, tipo: str, evaluacion_riesgo: EvaluacionRiesgo):
        self.numero_poliza = numero_poliza
        self.cliente = cliente
        self.tipo = tipo
        self.evaluacion_riesgo = evaluacion_riesgo
