from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.prospecto.adaptadores.tuplerows_prospecto_condominio_adapter import TupleRowsProspectoCondominioAdapter


class RepositorioProspectosPostgres(RepositorioProspectos):
    
    def registrar(self, prospecto: Prospecto) -> None:
        pass
    
    def buscar(self, id: int) -> Prospecto | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select P.id as id_prospecto,
                    P.rut_riesgo, P.nombre_riesgo,
                    P.fecha_registro as fecha_registro_prospecto,
                    P.telefono_contacto,
                    PCO.nombre_contacto, PCO.cargo_contacto,
                    P.correo_contacto,
                    PCO.tiene_locales_comerciales,
                    PCO.uso_del_condominio,
                    PCO.numero_pisos, PCO.numero_torres,
                    PCO.cantidad_departamentos, 
                    PCO.cantidad_subterraneos, PCO.tiene_piscina,
                    PCO.year_construccion, PCO.metros_cuadrados,
                    PCO.desea_ser_contactado,
                    EB.nombre as estado,
                    HE.fecha_registro as fecha_registro_estado,
                    EP.dias_limite_particular, 
                    EB.dias_limite as dias_limite_base,
                    extract(day from (now() - HE.fecha_registro)) AS dias_transcurridos
                    from Prospecto P
                    inner join ProspectoCondominio PCO
                    on P.id = PCO.id
                    inner join ProcesoComercial PC
                    on P.id = PC.id
                    inner join HistorialEstado HE
                    on PC.id = HE.id_proceso_comercial
                    inner join EstadoParticular EP
                    on HE.id_estado_particular = EP.id
                    inner join EstadoBase EB
                    on EP.codigo_estado_base = EB.codigo
                    where P.id = %(id)s
                '''
                params = {
                    'id': id
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                if rows is None or len(rows) == 0:
                    return None

                return TupleRowsProspectoCondominioAdapter(rows)

    def cambiar_siguiente_estado(self, id: int) -> None:
        pass