class RolResponsableTransicion:
    """Rol responsable de una transición principal.

    El responsable varía según el tipo de oportunidad: una misma
    transición puede tener roles distintos para oportunidades de
    renovación y nuevas, y más de un responsable por tipo.
    """

    def __init__(
        self,
        codigo_rol: str,
        renovacion: bool,
        id_transicion: int,
    ):
        self.codigo_rol = codigo_rol
        self.renovacion = renovacion
        self.id_transicion = id_transicion
