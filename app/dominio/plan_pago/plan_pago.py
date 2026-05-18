from app.dominio.cuota.cuota import Cuota


class PlanPago:
    def __init__(
        self,
        cuotas: list[Cuota],
        id: int | None = None
    ):
        self.id = id
        self.cuotas = cuotas