class DesgloseReconstruccionUnidad:
    """Desglose de reconstrucción calculado para una unidad de la alícuota.

    Valores derivados (nunca se persisten): varían cuando cambian los datos
    del condominio (m², UF/m², depreciación).

    `prorrateo` es la alícuota del administrador (por m² construidos, fija);
    `prorrateo_pago` es el prorrateo por monto asegurado
    (monto_asegurado_sugerido / total sugerido) que reparte las primas.
    """

    def __init__(
        self,
        identificador_unidad: str,
        prorrateo: float,
        fila_origen: int,
        monto_reconstruccion: float,
        monto_asegurado_sugerido: float,
        prorrateo_pago: float,
    ) -> None:
        self.identificador_unidad = identificador_unidad
        self.prorrateo = prorrateo
        self.fila_origen = fila_origen
        self.monto_reconstruccion = monto_reconstruccion
        self.monto_asegurado_sugerido = monto_asegurado_sugerido
        self.prorrateo_pago = prorrateo_pago

    def to_dict(self) -> dict:
        return {
            'identificador_unidad': self.identificador_unidad,
            'prorrateo': self.prorrateo,
            'fila_origen': self.fila_origen,
            'monto_reconstruccion': self.monto_reconstruccion,
            'monto_asegurado_sugerido': self.monto_asegurado_sugerido,
            'prorrateo_pago': self.prorrateo_pago,
        }
