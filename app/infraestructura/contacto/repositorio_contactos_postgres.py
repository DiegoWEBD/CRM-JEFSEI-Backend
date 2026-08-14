from app.dominio.contacto.contacto import Contacto
from app.dominio.contacto.repositorio_contactos import RepositorioContactos
from app.infraestructura.contacto.adaptadores.dictrow_contacto_adapter import (
    DictRowContactoAdapter,
)
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioContactosPostgres(RepositorioContactos):

    def obtener_por_prospecto(self, id_prospecto: int) -> list[Contacto]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = """
                    select id, id_prospecto, nombre, telefono, correo, cargo
                    from Contacto
                    where id_prospecto = %(id_prospecto)s
                    order by id
                """
                cur.execute(query, {"id_prospecto": id_prospecto})
                rows = cur.fetchall()

                if not rows:
                    return []

                return [
                    DictRowContactoAdapter(row).to_contacto()
                    for row in rows
                ]

    def buscar(self, id: int) -> Contacto | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = """
                    select id, id_prospecto, nombre, telefono, correo, cargo
                    from Contacto
                    where id = %(id)s
                """
                cur.execute(query, {"id": id})
                row = cur.fetchone()

                if row is None:
                    return None

                return DictRowContactoAdapter(row).to_contacto()

    def guardar(self, contacto: Contacto) -> Contacto:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = """
                    insert into Contacto (id_prospecto, nombre, telefono, correo, cargo)
                    values (%(id_prospecto)s, %(nombre)s, %(telefono)s, %(correo)s, %(cargo)s)
                    returning id
                """
                cur.execute(query, {
                    'id_prospecto': contacto.id_prospecto,
                    'nombre': contacto.nombre,
                    'telefono': contacto.telefono,
                    'correo': contacto.correo,
                    'cargo': contacto.cargo,
                })
                contacto.id = cur.fetchone()['id']
                return contacto

    def actualizar(self, contacto: Contacto) -> Contacto:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = """
                    update Contacto
                    set nombre = %(nombre)s,
                        telefono = %(telefono)s,
                        correo = %(correo)s,
                        cargo = %(cargo)s
                    where id = %(id)s
                """
                cur.execute(query, {
                    'id': contacto.id,
                    'nombre': contacto.nombre,
                    'telefono': contacto.telefono,
                    'correo': contacto.correo,
                    'cargo': contacto.cargo,
                })
                return contacto

    def eliminar(self, id: int) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = """
                    delete from Contacto
                    where id = %(id)s
                """
                cur.execute(query, {"id": id})
                return cur.rowcount > 0