class RefreshTokenInvalidoError(Exception):
    """El refresh token no existe, está expirado o la sesión fue revocada."""
    pass


class RefreshTokenReusadoError(Exception):
    """Se detectó reutilización de un refresh token ya rotado.

    Esto indica posible robo: toda la familia de tokens ha sido revocada.
    """
    pass
