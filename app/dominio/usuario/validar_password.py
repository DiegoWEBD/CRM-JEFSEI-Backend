"""Política de fortaleza de contraseñas.

Reglas (deben mantenerse en paridad con frontend/src/lib/validacion-password.ts):
- de 12 a 72 caracteres (72 bytes es el límite duro de bcrypt: valores mayores
  se truncan silenciosamente y dos contraseñas distintas podrían coincidir)
- al menos una letra mayúscula, una letra minúscula y un dígito
- no pertenecer a la lista de contraseñas comunes
"""

from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException

LONGITUD_MINIMA = 12
LONGITUD_MAXIMA_BYTES = 72

# Contraseñas frecuentes que cumplen las reglas de longitud y clases pero son
# predecibles. Se comparan en minúsculas.
CONTRASENAS_COMUNES = frozenset({
    '123456789012',
    'password123',
    'password1234',
    'password12345',
    'passw0rd123',
    'passw0rd1234',
    'admin123456',
    'admin1234567',
    'administrator1',
    'qwerty123456',
    'qwertyuiop123',
    'asdfghjkl123',
    'zxcvbnm12345',
    'welcome12345',
    'welcome123456',
    'letmein12345',
    'letmein123456',
    'iloveyou1234',
    'iloveyou12345',
    'monkey123456',
    'dragon123456',
    'sunshine1234',
    'princess1234',
    'football1234',
    'baseball1234',
    'superman1234',
    'starwars1234',
    'trustno12345',
    'whatever1234',
    'michael12345',
    'shadow123456',
    'master123456',
    'jennifer1234',
    'jordan123456',
    'contrasena123',
    'clave1234567',
    'seguridad123',
})


def validar_fortaleza_password(password: str) -> None:
    """Valida la fortaleza de la contraseña; lanza DatoInvalidoException si no cumple."""
    if not isinstance(password, str) or len(password) < LONGITUD_MINIMA:
        raise DatoInvalidoException(
            f'La contraseña debe tener al menos {LONGITUD_MINIMA} caracteres'
        )
    if len(password.encode('utf-8')) > LONGITUD_MAXIMA_BYTES:
        raise DatoInvalidoException('La contraseña no puede exceder 72 caracteres')
    if not any(c.isupper() for c in password):
        raise DatoInvalidoException('La contraseña debe incluir al menos una letra mayúscula')
    if not any(c.islower() for c in password):
        raise DatoInvalidoException('La contraseña debe incluir al menos una letra minúscula')
    if not any(c.isdigit() for c in password):
        raise DatoInvalidoException('La contraseña debe incluir al menos un dígito')
    if password.lower() in CONTRASENAS_COMUNES:
        raise DatoInvalidoException('La contraseña es demasiado común; elija otra')
