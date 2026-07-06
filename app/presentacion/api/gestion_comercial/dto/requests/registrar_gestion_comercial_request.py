from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator, model_validator


TIPO_GESTION = Literal['llamada', 'correo', 'visita', 'mensaje']

ESTADOS_CONTACTO_LLAMADA: set[str] = {
    'no_contesta',
    'pide_contacto_despues',
    'pendiente de respuesta',
    'no interesado por ahora',
    'sin respuesta tras seguimiento',
}


class RegistrarGestionComercialRequest(BaseModel):
    tipo: TIPO_GESTION
    id_prospecto: int
    titulo: str
    estado_contacto: str | None = None
    observacion: str | None = None
    fecha_gestion: datetime

    @field_validator('titulo')
    @classmethod
    def titulo_no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('El título no puede estar vacío')
        return v.strip()

    @model_validator(mode='after')
    def validar_estado_contacto(self) -> 'RegistrarGestionComercialRequest':
        if self.tipo != 'llamada':
            self.estado_contacto = None
        elif self.estado_contacto is not None and self.estado_contacto not in ESTADOS_CONTACTO_LLAMADA:
            raise ValueError(
                f'estado_contacto inválido para llamada: "{self.estado_contacto}". '
                f'Valores válidos: {", ".join(sorted(ESTADOS_CONTACTO_LLAMADA))}'
            )
        return self
