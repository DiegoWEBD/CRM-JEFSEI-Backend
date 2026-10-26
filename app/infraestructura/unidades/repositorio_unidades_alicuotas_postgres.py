from psycopg import sql

from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.validador_alicuotas import (
    normalizar_clave_identificador,
)
from app.dominio.unidades.repositorio_unidades_alicuotas import RepositorioUnidadesAlicuotas
from app.dominio.unidades.unidad_alicuota import UnidadAlicuota
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.unidades.adaptadores.dictrow_unidad_alicuota_adapter import DictRowUnidadAlicuotaAdapter


class RepositorioUnidadesAlicuotasPostgres(RepositorioUnidadesAlicuotas):

    COLUMNAS = sql.SQL(', ').join(
        sql.Identifier(columna)
        for columna in (
            'id',
            'identificador_unidad',
            'prorrateo',
            'fila_origen',
            'descartada',
            'monto_asegurado_personalizado',
        )
    )

    def listar_por_oportunidad(self, id_proceso_comercial: int) -> list[UnidadAlicuota]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = sql.SQL('''
                    select {columnas}
                    from ProcesoComercialUnidad
                    where id_proceso_comercial = %(id_proceso_comercial)s
                    order by fila_origen, id
                ''').format(columnas=self.COLUMNAS)

                params = {
                    'id_proceso_comercial': id_proceso_comercial
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                return [
                    DictRowUnidadAlicuotaAdapter(row).to_unidad_alicuota()
                    for row in rows
                ]

    def buscar_por_id(self, id_unidad: int, id_proceso_comercial: int) -> UnidadAlicuota | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = sql.SQL('''
                    select {columnas}
                    from ProcesoComercialUnidad
                    where id = %(id_unidad)s
                    and id_proceso_comercial = %(id_proceso_comercial)s
                ''').format(columnas=self.COLUMNAS)

                params = {
                    'id_unidad': id_unidad,
                    'id_proceso_comercial': id_proceso_comercial,
                }

                cur.execute(query, params)
                row = cur.fetchone()

                return DictRowUnidadAlicuotaAdapter(row).to_unidad_alicuota() if row is not None else None

    def obtener_nombre_excel(self, id_proceso_comercial: int) -> str | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select nombre_excel_alicuota
                    from ProcesoComercial
                    where id = %(id_proceso_comercial)s
                '''

                params = {
                    'id_proceso_comercial': id_proceso_comercial
                }

                cur.execute(query, params)
                row = cur.fetchone()

                return row['nombre_excel_alicuota'] if row is not None else None

    def guardar_o_reemplazar(
        self,
        id_proceso_comercial: int,
        nombre_excel: str,
        unidades: list[UnidadAlicuota],
    ) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                # La configuración por unidad (descarte y monto personalizado)
                # se preserva al reemplazar la importación: si el identificador
                # de la unidad vuelve a aparecer en el archivo nuevo, mantiene
                # lo ya configurado en el sistema.
                cur.execute('''
                    select identificador_unidad, descartada, monto_asegurado_personalizado
                    from ProcesoComercialUnidad
                    where id_proceso_comercial = %(id_proceso_comercial)s
                ''', {'id_proceso_comercial': id_proceso_comercial})

                configuracion_previa: dict[str, dict] = {}

                for row in cur.fetchall():
                    clave = normalizar_clave_identificador(row['identificador_unidad'])
                    configuracion_previa[clave] = {
                        'descartada': row['descartada'],
                        'monto_asegurado_personalizado': row['monto_asegurado_personalizado'],
                    }

                cur.execute('''
                    delete from ProcesoComercialUnidad
                    where id_proceso_comercial = %(id_proceso_comercial)s
                ''', {'id_proceso_comercial': id_proceso_comercial})

                for unidad in unidades:
                    previa = configuracion_previa.get(
                        normalizar_clave_identificador(unidad.identificador_unidad)
                    )

                    cur.execute('''
                        insert into ProcesoComercialUnidad
                            (id_proceso_comercial, identificador_unidad, prorrateo, fila_origen,
                             descartada, monto_asegurado_personalizado)
                        values (%(id_proceso_comercial)s, %(identificador_unidad)s, %(prorrateo)s, %(fila_origen)s,
                                %(descartada)s, %(monto_asegurado_personalizado)s)
                    ''', {
                        'id_proceso_comercial': id_proceso_comercial,
                        'identificador_unidad': unidad.identificador_unidad,
                        'prorrateo': unidad.prorrateo,
                        'fila_origen': unidad.fila_origen,
                        'descartada': unidad.descartada if previa is None else previa['descartada'],
                        'monto_asegurado_personalizado': (
                            unidad.monto_asegurado_personalizado
                            if previa is None
                            else previa['monto_asegurado_personalizado']
                        ),
                    })

                cur.execute('''
                    update ProcesoComercial
                    set nombre_excel_alicuota = %(nombre_excel)s
                    where id = %(id_proceso_comercial)s
                ''', {
                    'nombre_excel': nombre_excel,
                    'id_proceso_comercial': id_proceso_comercial,
                })

    def actualizar_unidades(self, unidades: list[UnidadAlicuota]) -> None:
        # Todos los updates comparten la misma conexión: o se aplican todas
        # las unidades del lote o no se aplican ninguna.
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                for unidad in unidades:
                    cur.execute('''
                        update ProcesoComercialUnidad
                        set descartada = %(descartada)s,
                            monto_asegurado_personalizado = %(monto_asegurado_personalizado)s
                        where id = %(id_unidad)s
                    ''', {
                        'id_unidad': unidad.id,
                        'descartada': unidad.descartada,
                        'monto_asegurado_personalizado': unidad.monto_asegurado_personalizado,
                    })
