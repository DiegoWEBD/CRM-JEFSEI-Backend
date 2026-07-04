from app.dominio.recordatorio.recordatorio_renovacion_poliza.recordatorio_renovacion_poliza import RecordatorioRenovacionPoliza
from app.dominio.recordatorio.recordatorio_usuario.recordatorio_usuario import RecordatorioUsuario
from app.dominio.recordatorio.repositorio_recordatorios import RepositorioRecordatorios

from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.recordatorio.adaptadores.dictrow_recordatorio_renovacion_poliza_adapter import DictRowRecordatorioRenovacionPolizaAdapter
from app.infraestructura.recordatorio.adaptadores.dictrow_recordatorio_usuario_adapter import DictRowRecordatorioUsuarioAdapter


class RepositorioRecordatoriosPostgres(RepositorioRecordatorios):

    def registrar(self, rut_usuario: str, titulo: str, detalle: str | None, prioridad: str, tipo_gestion: str, fecha_recordatorio: str, id_prospecto: int | None) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    insert into Recordatorio (titulo, detalle, completado, prioridad, tipo_gestion, fecha_recordatorio)
                    values (%(titulo)s, %(detalle)s, false, %(prioridad)s, %(tipo_gestion)s, %(fecha_recordatorio)s::timestamptz)
                    returning id
                '''
                params = {
                    'titulo': titulo,
                    'detalle': detalle,
                    'prioridad': prioridad,
                    'tipo_gestion': tipo_gestion,
                    'fecha_recordatorio': fecha_recordatorio
                }

                cur.execute(query, params)
                row = cur.fetchone()

                id = row['id'] # type: ignore

                query = '''
                    insert into RecordatorioUsuario (id, rut_usuario, id_prospecto)
                    values (%(id)s, %(rut_usuario)s, %(id_prospecto)s)
                '''
                params = {
                    'id': id,
                    'rut_usuario': rut_usuario,
                    'id_prospecto': id_prospecto
                }

                cur.execute(query, params)
                

    def obtener_recordatorios_usuario(self, rut_usuario: str, fecha: str, id_prospecto: int | None) -> list[RecordatorioUsuario]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select R.id,
                    RU.id_prospecto,
                    P.nombre_riesgo,
                    R.titulo,
                    R.detalle,
                    R.completado,
                    R.tipo_gestion,
                    R.prioridad,
                    R.fecha_recordatorio
                    from RecordatorioUsuario RU
                    inner join Recordatorio R
                    on RU.id = R.id
                    left join Prospecto P
                    on RU.id_prospecto = P.id
                    where RU.rut_usuario = %(rut_usuario)s
                    and R.completado = false
                    and R.fecha_recordatorio < (%(fecha)s::date + interval '1 day')
                '''

                params = {
                    'rut_usuario': rut_usuario,
                    'fecha': fecha
                }

                if id_prospecto is not None:
                    query += ' and P.id = %(id_prospecto)s'
                    params['id_prospecto'] = str(id_prospecto)

                query += ' order by R.fecha_recordatorio'
                cur.execute(query, params)

                rows = cur.fetchall()

                return [DictRowRecordatorioUsuarioAdapter(row).to_recordatorio()for row in rows]
            
    def obtener_recordatorios_renovacion(self, rut_usuario: str, fecha: str, id_prospecto: int | None) -> list[RecordatorioRenovacionPoliza]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select R.id,
                    RR.numero_poliza,
                    R.titulo,
                    R.detalle,
                    R.completado,
                    R.tipo_gestion,
                    R.prioridad,
                    R.fecha_recordatorio
                    from RecordatorioRenovacionPoliza RR
                    inner join Recordatorio R
                    on RR.id = R.id
                    inner join Poliza P
                    on RR.numero_poliza = P.numero_poliza
                    inner join Cliente C
                    on P.id_cliente = C.id
                    where R.completado = false
                    and R.fecha_recordatorio < (%(fecha)s::date + interval '1 day')
                    and (
                        C.rut_ej_renovacion_asignado = %(rut_usuario)s
                        or C.rut_as_renovacion_asignado = %(rut_usuario)s
                    )
                '''

                params = {
                    'rut_usuario': rut_usuario,
                    'fecha': fecha
                }

                if id_prospecto is not None:
                    query += ' and P.id = %(id_prospecto)s'
                    params['id_prospecto'] = str(id_prospecto)

                query += ' order by R.fecha_recordatorio'
                cur.execute(query, params)

                rows = cur.fetchall()

                return [DictRowRecordatorioRenovacionPolizaAdapter(row).to_recordatorio()for row in rows]