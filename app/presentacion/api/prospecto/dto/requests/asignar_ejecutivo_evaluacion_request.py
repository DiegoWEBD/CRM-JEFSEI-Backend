from pydantic import BaseModel


class AsignarEjecutivoEvaluacionRequest(BaseModel):
    rut_ej_evaluacion: str