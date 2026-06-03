from app.dominio.recordatorio.repositorio_recordatorios import RepositorioRecordatorios

from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.recordatorio.adaptadores.dictrow_recordatorio_adapter import DictRowRecordatorioAdapter


class RepositorioRecordatoriosPostgres(RepositorioRecordatorios):

    def obtener_recordatorios(self, rut_usuario: str, fecha: str, id_prospecto: int | None):
        print(f'Fecha: {fecha}')

        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select RU.id,
                    RU.id_prospecto,
                    P.nombre_riesgo,
                    RU.titulo,
                    RU.detalle,
                    RU.completado,
                    RU.tipo_gestion,
                    RU.prioridad,
                    RU.fecha_recordatorio
                    from RecordatorioUsuario RU
                    left join Prospecto P
                    on RU.id_prospecto = P.id
                    where RU.rut_usuario = %(rut_usuario)s
                    and RU.fecha_recordatorio >= %(fecha)s
                    and RU.fecha_recordatorio < (%(fecha)s::date + interval '1 day')
                '''

                params = {
                    'rut_usuario': rut_usuario,
                    'fecha': fecha
                }

                if id_prospecto is not None:
                    query += ' and P.id = %(id_prospecto)s'
                    params['id_prospecto'] = str(id_prospecto)

                cur.execute(query, params)

                rows = cur.fetchall()

                return [DictRowRecordatorioAdapter(row).to_recordatorio()for row in rows]