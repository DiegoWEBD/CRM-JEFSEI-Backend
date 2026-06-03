from pydantic import BaseModel


class ObtenerRecordatoriosRequest(BaseModel):
    fecha: str
    id_prospecto: int | None