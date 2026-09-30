from dataclasses import dataclass


@dataclass
class RotarSesionResponseDTO:
    """Respuesta de POST /auth/refresh.

    ``refresh_token`` viene vacío cuando la rotación resultó ser duplicada
    dentro de la ventana de gracia: ahí el cliente ya recibió el par de la
    llamada original y no necesita otro, así que no se le manda un token en
    blanco para que lo sobreescriba.
    """

    access_token: str
    refresh_token: str
    id_sesion: str
    expire_minutes: int
    token_type: str = 'bearer'
