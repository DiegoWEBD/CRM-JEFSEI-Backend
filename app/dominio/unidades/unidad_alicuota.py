class UnidadAlicuota:
    """Unidad de la alícuota importada desde el Excel del administrador.

    `prorrateo` es la alícuota del administrador (fracción decimal del todo:
    0.0085 representa 0.85 %). La configuración de procesamiento de cada
    unidad se administra desde el sistema:

    - `descartada`: la unidad se excluye del procesamiento sin eliminarla.
    - `monto_asegurado_personalizado`: monto asegurado (UF) fijado
      explícitamente; cuando es None se usa el monto sugerido por el sistema.
    """

    def __init__(
        self,
        identificador_unidad: str,
        prorrateo: float,
        fila_origen: int,
        id: int | None = None,
        descartada: bool = False,
        monto_asegurado_personalizado: float | None = None,
    ) -> None:
        self.id = id
        self.identificador_unidad = identificador_unidad
        self.prorrateo = prorrateo
        self.fila_origen = fila_origen
        self.descartada = descartada
        self.monto_asegurado_personalizado = monto_asegurado_personalizado

    @property
    def tiene_monto_asegurado_personalizado(self) -> bool:
        return self.monto_asegurado_personalizado is not None

    def monto_asegurado_efectivo(self, monto_asegurado_sugerido: float | None = None) -> float | None:
        """Monto asegurado de la unidad: el personalizado si existe, si no el sugerido."""

        if self.monto_asegurado_personalizado is not None:
            return self.monto_asegurado_personalizado

        return monto_asegurado_sugerido

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'identificador_unidad': self.identificador_unidad,
            'prorrateo': self.prorrateo,
            'fila_origen': self.fila_origen,
            'descartada': self.descartada,
            'monto_asegurado_personalizado': self.monto_asegurado_personalizado,
            'tiene_monto_asegurado_personalizado': self.tiene_monto_asegurado_personalizado,
        }
