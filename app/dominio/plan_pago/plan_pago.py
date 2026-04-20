from datetime import datetime

class PlanPago:
    def __init__(self, numero_cuotas: int, monto_por_cuota: float, fecha_primera_cuota: datetime):
        self.numero_cuotas = numero_cuotas
        self.monto_por_cuota = monto_por_cuota
        self.fecha_primera_cuota = fecha_primera_cuota