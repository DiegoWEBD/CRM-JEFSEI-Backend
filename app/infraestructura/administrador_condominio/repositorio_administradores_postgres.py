from app.dominio.administrador_condominio.administrador_condominio import (
    AdministradorCondominio,
)
from app.dominio.administrador_condominio.repositorio_administradores import (
    RepositorioAdministradores,
)
from app.infraestructura.administrador_condominio.adaptadores.dictrow_administrador_adapter import (
    DictRowAdministradorAdapter,
)
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioAdministradoresPostgres(RepositorioAdministradores):

    def obtener_todos(self) -> list[AdministradorCondominio]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = """
                    select id, nombre_administrador, nombre_contacto, telefono, correo
                    from AdministradorCondominio
                    order by nombre_administrador
                """
                cur.execute(query)
                rows = cur.fetchall()

                if not rows:
                    return []

                return [
                    DictRowAdministradorAdapter(row).to_administrador()
                    for row in rows
                ]

    def buscar(self, id: int) -> AdministradorCondominio | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = """
                    select id, nombre_administrador, nombre_contacto, telefono, correo
                    from AdministradorCondominio
                    where id = %(id)s
                """
                cur.execute(query, {"id": id})
                row = cur.fetchone()

                if row is None:
                    return None

                return DictRowAdministradorAdapter(row).to_administrador()

    def guardar(self, administrador: AdministradorCondominio) -> AdministradorCondominio:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = """
                    INSERT INTO AdministradorCondominio (nombre_administrador, nombre_contacto, telefono, correo)
                    VALUES (%(nombre_administrador)s, %(nombre_contacto)s, %(telefono)s, %(correo)s)
                    RETURNING id
                """
                cur.execute(query, {
                    'nombre_administrador': administrador.nombre_administrador,
                    'nombre_contacto': administrador.nombre_contacto,
                    'telefono': administrador.telefono,
                    'correo': administrador.correo,
                })
                administrador.id = cur.fetchone()['id']
                return administrador

    def actualizar(self, administrador: AdministradorCondominio) -> AdministradorCondominio:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = """
                    UPDATE AdministradorCondominio
                    SET nombre_administrador = %(nombre_administrador)s,
                        nombre_contacto = %(nombre_contacto)s,
                        telefono = %(telefono)s,
                        correo = %(correo)s
                    WHERE id = %(id)s
                """
                cur.execute(query, {
                    'id': administrador.id,
                    'nombre_administrador': administrador.nombre_administrador,
                    'nombre_contacto': administrador.nombre_contacto,
                    'telefono': administrador.telefono,
                    'correo': administrador.correo,
                })
                return administrador
