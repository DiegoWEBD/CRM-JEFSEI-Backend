from dataclasses import dataclass


@dataclass
class ContextoPeticion:
    ip_origen: str
    user_agent: str | None = None
    id_peticion: str | None = None
