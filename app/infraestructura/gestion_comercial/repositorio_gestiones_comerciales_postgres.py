from datetime import datetime, timezone

from app.dominio.gestion_comercial.gestion_comercial import GestionComercial
from app.dominio.gestion_comercial.repositorio_gestiones_comerciales import RepositorioGestionesComerciales
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.gestion_comercial.adaptadores.dictrow_gestion_comercial_adapter import DictRowGestionComercialAdapter


class RepositorioGestionesComercialesPostgres(RepositorioGestionesComerciales):

    def registrar(
        self,
        tipo: str,
        rut_usuario: str,
        id_prospecto: int,
        titulo: str,
        estado_contacto: str | None,
        observacion: str | None,
        fecha_gestion: datetime,
    ) -> GestionComercial:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                created_at = datetime.now(timezone.utc)

                cur.execute(
                    """
                    insert into GestionComercial (tipo, rut_usuario, id_prospecto, titulo, estado_contacto, observacion, created_at, fecha_gestion)
                    values (%(tipo)s, %(rut_usuario)s, %(id_prospecto)s, %(titulo)s, %(estado_contacto)s, %(observacion)s, %(created_at)s, %(fecha_gestion)s)
                    returning id
                    """,
                    {
                        "tipo": tipo,
                        "rut_usuario": rut_usuario,
                        "id_prospecto": id_prospecto,
                        "titulo": titulo,
                        "estado_contacto": estado_contacto,
                        "observacion": observacion,
                        "created_at": created_at,
                        "fecha_gestion": fecha_gestion,
                    },
                )
                row = cur.fetchone()
                if row is None:
                    raise RuntimeError("No se pudo crear la gestión comercial")
                id_creado: int = row["id"]

        return self._buscar_por_id(id_creado)

    def obtener_todas(self, id_prospecto: int | None = None) -> list[GestionComercial]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = """
                    select
                        GC.id,
                        GC.tipo,
                        GC.rut_usuario,
                        U.nombre as nombre_ejecutivo,
                        GC.id_prospecto,
                        PR.nombre_riesgo as nombre_cliente,
                        GC.titulo,
                        GC.estado_contacto,
                        GC.observacion,
                        GC.created_at,
                        GC.fecha_gestion
                    from GestionComercial GC
                    left join Usuario U on GC.rut_usuario = U.rut
                    left join Prospecto PR on GC.id_prospecto = PR.id
                    where 1 = 1
                """
                params: list = []

                if id_prospecto is not None:
                    query += " and GC.id_prospecto = %s"
                    params.append(id_prospecto)

                query += " order by GC.fecha_gestion desc"

                cur.execute(query, params)
                rows = cur.fetchall()

                return [DictRowGestionComercialAdapter(row).to_gestion_comercial() for row in rows]

    def obtener_ultima(self, id_prospecto: int) -> GestionComercial | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select
                        GC.id,
                        GC.tipo,
                        GC.rut_usuario,
                        U.nombre as nombre_ejecutivo,
                        GC.id_prospecto,
                        PR.nombre_riesgo as nombre_cliente,
                        GC.titulo,
                        GC.estado_contacto,
                        GC.observacion,
                        GC.created_at,
                        GC.fecha_gestion
                    from GestionComercial GC
                    left join Usuario U on GC.rut_usuario = U.rut
                    left join Prospecto PR on GC.id_prospecto = PR.id
                    where GC.id_prospecto = %s
                    order by GC.created_at desc
                    limit 1
                    """,
                    [id_prospecto],
                )
                row = cur.fetchone()

                return DictRowGestionComercialAdapter(row).to_gestion_comercial() if row else None

    def _buscar_por_id(self, id: int) -> GestionComercial:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select
                        GC.id,
                        GC.tipo,
                        GC.rut_usuario,
                        U.nombre as nombre_ejecutivo,
                        GC.id_prospecto,
                        PR.nombre_riesgo as nombre_cliente,
                        GC.titulo,
                        GC.estado_contacto,
                        GC.observacion,
                        GC.created_at,
                        GC.fecha_gestion
                    from GestionComercial GC
                    left join Usuario U on GC.rut_usuario = U.rut
                    left join Prospecto PR on GC.id_prospecto = PR.id
                    where GC.id = %s
                    """,
                    [id],
                )
                row = cur.fetchone()
                if row is None:
                    raise RuntimeError(f"Gestión comercial con id {id} no encontrada después de crear")
                return DictRowGestionComercialAdapter(row).to_gestion_comercial()
