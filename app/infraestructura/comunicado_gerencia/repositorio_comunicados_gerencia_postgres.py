from app.dominio.comunicado_gerencia.comunicado_gerencia import ComunicadoGerencia
from app.dominio.comunicado_gerencia.repositorio_comunicados_gerencia import RepositorioComunicadosGerencia
from app.infraestructura.comunicado_gerencia.adaptadores.dictrow_comunicado_gerencia_adapter import DictRowComunicadoGerenciaAdapter
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioComunicadosGerenciaPostgres(RepositorioComunicadosGerencia):

    def obtener_todos(self) -> list[ComunicadoGerencia]:
        
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select CG.id, CG.titulo, 
                    CG.descripcion, CG.prioridad,
                    CG.fecha, U.nombre as nombre_gerente, 
                    CG.caducidad
                    from ComunicadoGerencia CG
                    inner join Usuario U
                    on CG.rut_gerente = U.rut
                    where CG.caducidad >= current_timestamp
                '''

                cur.execute(query)
                rows = cur.fetchall()

                return [DictRowComunicadoGerenciaAdapter(row).to_comunicado_gerencia() for row in rows]

    def registrar(self, comunicado: ComunicadoGerencia, rut_gerente: str) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    insert into ComunicadoGerencia (rut_gerente, titulo, descripcion, prioridad, fecha, caducidad)
                    values (%(rut_gerente)s, %(titulo)s, %(descripcion)s, %(prioridad)s, %(fecha)s, %(caducidad)s)
                '''
                params = {
                    'rut_gerente': rut_gerente,
                    'titulo': comunicado.titulo,
                    'descripcion': comunicado.descripcion,
                    'prioridad': comunicado.prioridad,
                    'fecha': comunicado.fecha,
                    'caducidad': comunicado.caducidad
                }

                cur.execute(query, params)
                return True