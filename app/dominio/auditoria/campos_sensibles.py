"""Campos que jamás se guardan en claro dentro de un registro de auditoría.

La lista es central y se aplica recursivamente a datos_antes, datos_despues,
cambios y metadata, incluyendo claves anidadas dentro de listas y diccionarios.
"""

CAMPOS_SENSIBLES: frozenset[str] = frozenset({
    'password',
    'password_hash',
    'passwordHash',
    'contrasena',
    'contraseña',
    'token',
    'access_token',
    'accessToken',
    'refresh_token',
    'refreshToken',
    'jwt',
    'authorization',
    'cookie',
    'set-cookie',
    'secret',
    'api_key',
    'apiKey',
    'token_hash',
    'tarjeta',
    'numero_tarjeta',
    'card_number',
    'cvv',
})

# Sustitución aplicada en lugar del valor. La auditoría deja claro que había un
# dato ahí sin filtrarlo.
VALOR_REDACTADO = '[REDACTED]'
