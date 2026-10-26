class DesgloseReconstruccionUnidad:
    """Desglose de reconstrucción calculado para una unidad de la alícuota.

    Valores derivados (nunca se persisten): varían cuando cambian los datos
    del condominio (m², UF/m², depreciación) o la configuración de la unidad.

    `prorrateo` es la alícuota del administrador (por m² construidos, fija);
    `prorrateo_pago` es el prorrateo por monto asegurado (monto asegurado de
    la unidad sobre el total de las unidades activas) que reparte las primas.

    `monto_asegurado` es el monto efectivo de la unidad: el personalizado si
    existe, si no el sugerido. `descartada` marca las unidades excluidas del
    procesamiento: no aportan al total y su `prorrateo_pago` es 0.
    """

    def __init__(
        self,
        identificador_unidad: str,
        prorrateo: float,
        fila_origen: int,
        monto_reconstruccion: float,
        monto_asegurado_sugerido: float,
        prorrateo_pago: float,
        id_unidad: int | None = None,
        descartada: bool = False,
        monto_asegurado: float | None = None,
        monto_asegurado_personalizado: float | None = None,
    ) -> None:
        self.id_unidad = id_unidad
        self.identificador_unidad = identificador_unidad
        self.prorrateo = prorrateo
        self.fila_origen = fila_origen
        self.monto_reconstruccion = monto_reconstruccion
        self.monto_asegurado_sugerido = monto_asegurado_sugerido
        self.monto_asegurado_personalizado = monto_asegurado_personalizado
        self.monto_asegurado = (
            monto_asegurado
            if monto_asegurado is not None
            else (monto_asegurado_personalizado if monto_asegurado_personalizado is not None else monto_asegurado_sugerido)
        )
        self.prorrateo_pago = prorrateo_pago
        self.descartada = descartada

    @property
    def tiene_monto_asegurado_personalizado(self) -> bool:
        return self.monto_asegurado_personalizado is not None

    def to_dict(self) -> dict:
        return {
            'id_unidad': self.id_unidad,
            'identificador_unidad': self.identificador_unidad,
            'prorrateo': self.prorrateo,
            'fila_origen': self.fila_origen,
            'monto_reconstruccion': self.monto_reconstruccion,
            'monto_asegurado_sugerido': self.monto_asegurado_sugerido,
            'monto_asegurado': self.monto_asegurado,
            'monto_asegurado_personalizado': self.monto_asegurado_personalizado,
            'tiene_monto_asegurado_personalizado': self.tiene_monto_asegurado_personalizado,
            'prorrateo_pago': self.prorrateo_pago,
            'descartada': self.descartada,
        }
