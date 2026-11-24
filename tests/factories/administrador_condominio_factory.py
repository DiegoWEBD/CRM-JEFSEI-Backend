from app.dominio.administrador_condominio.administrador_condominio import (
    AdministradorCondominio,
)


def crear_administrador_mock(
    id: int | None = 1,
    nombre_administrador: str = "Administrador Test",
    nombre_contacto: str | None = "Contacto Test",
    telefono: str | None = "+56912345678",
    correo: str | None = "admin.condominio@test.com",
) -> AdministradorCondominio:
    return AdministradorCondominio(
        id=id,
        nombre_administrador=nombre_administrador,
        nombre_contacto=nombre_contacto,
        telefono=telefono,
        correo=correo,
    )
