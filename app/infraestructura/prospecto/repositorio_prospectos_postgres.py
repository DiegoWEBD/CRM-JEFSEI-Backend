from psycopg import Cursor
from psycopg.rows import TupleRow

from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.prospecto.adaptadores.tuplerows_prospecto_condominio_adapter import TupleRowsProspectoCondominioAdapter


class RepositorioProspectosPostgres(RepositorioProspectos):
    
    def registrar_prospecto_condominio(self, prospecto: ProspectoCondominio) -> None:

        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                # Prospecto base
                query = '''
                    insert into Prospecto(
                        rut_riesgo,
                        nombre_riesgo,
                        nombre_contacto,
                        telefono_contacto,
                        correo_contacto,
                        direccion,
                        id_comuna,
                        observaciones,
                        id_linea_negocio,
                        rut_registrado_por
                    )
                    values(
                        %(rut_riesgo)s,
                        %(nombre_riesgo)s,
                        %(nombre_contacto)s,
                        %(telefono_contacto)s,
                        %(correo_contacto)s,
                        %(direccion)s,
                        %(id_comuna)s,
                        %(observaciones)s,
                        %(id_linea_negocio)s,
                        %(rut_registrado_por)s
                    )
                    returning id
                '''

                params = {
                    'rut_riesgo': prospecto.rut_riesgo,
                    'nombre_riesgo': prospecto.nombre_riesgo,
                    'nombre_contacto': prospecto.nombre_contacto,
                    'telefono_contacto': prospecto.telefono_contacto,
                    'correo_contacto': prospecto.correo_contacto,
                    'direccion': prospecto.direccion,
                    'id_comuna': prospecto.comuna.id,
                    'observaciones': prospecto.observaciones,
                    'id_linea_negocio': prospecto.linea_negocio.id,
                    'rut_registrado_por': prospecto.registrado_por.rut,
                }

                cur.execute(query, params)
                id_prospecto: int = cur.fetchone()['id']

                # Prospecto condominio
                query = '''
                    insert into ProspectoCondominio(
                        id,
                        cargo_contacto,
                        tiene_locales_comerciales,
                        uso_del_condominio,
                        numero_pisos,
                        numero_torres,
                        cantidad_departamentos,
                        cantidad_subterraneos,
                        tiene_piscina,
                        year_construccion,
                        metros_cuadrados,
                        desea_ser_contactado
                    )
                    values(
                        %(id)s,
                        %(cargo_contacto)s,
                        %(tiene_locales_comerciales)s,
                        %(uso_del_condominio)s,
                        %(numero_pisos)s,
                        %(numero_torres)s,
                        %(cantidad_departamentos)s,
                        %(cantidad_subterraneos)s,
                        %(tiene_piscina)s,
                        %(year_construccion)s,
                        %(metros_cuadrados)s,
                        %(desea_ser_contactado)s
                    )
                '''

                params = {
                    'id': id_prospecto,
                    'cargo_contacto': prospecto.cargo_contacto,
                    'tiene_locales_comerciales': prospecto.tiene_locales_comerciales,
                    'uso_del_condominio': prospecto.uso_del_condominio,
                    'numero_pisos': prospecto.numero_pisos,
                    'numero_torres': prospecto.numero_torres,
                    'cantidad_departamentos': prospecto.cantidad_departamentos,
                    'cantidad_subterraneos': prospecto.cantidad_subterraneos,
                    'tiene_piscina': prospecto.tiene_piscina,
                    'year_construccion': prospecto.year_construccion,
                    'metros_cuadrados': prospecto.metros_cuadrados,
                    'desea_ser_contactado': prospecto.desea_ser_contactado
                }

                cur.execute(query, params)

                # Proceso comercial
                query = '''
                    insert into ProcesoComercial(id_prospecto)
                    values (%(id_prospecto)s)
                    returning id
                '''           

                params = {
                    'id_prospecto': id_prospecto
                }     

                cur.execute(query, params)
                id_proceso_comercial: int = cur.fetchone()['id']

                # Estado inicial
                query = '''
                    insert into EstadoParticular(codigo_estado_base)
                    values ('PROSPECTO_CARGADO')
                    returning id
                '''               

                cur.execute(query)
                id_estado_particular: int = cur.fetchone()['id']

                # Registro histórico del estado
                query = '''
                    insert into HistorialEstado(id_proceso_comercial, id_estado_particular)
                    values(%(id_proceso_comercial)s, %(id_estado_particular)s)
                '''           

                params = {
                    'id_proceso_comercial': id_proceso_comercial,
                    'id_estado_particular': id_estado_particular
                }     

                cur.execute(query, params)

    
    def buscar(self, id: int) -> Prospecto | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select LN.nombre as linea_negocio
                    from Prospecto P
                    inner join LineaNegocio LN
                    on P.id_linea_negocio = LN.id
                    where P.id = %(id)s
                '''

                params = {
                    'id': id
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    return None
                
                linea_negocio = row['linea_negocio']

                if linea_negocio.lower() == 'condominio':
                    return self.__obtener_prospecto_condominio(id, cur)
                
                return None
                
    def asignar_ejecutivo_comercial(self, prospecto: Prospecto) -> None:
        if prospecto.id is None or prospecto.evaluacion_riesgo is None:
            return
        
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select id
                    from ProcesoComercial
                    where id_prospecto = %(id_prospecto)s
                '''
                params = {
                    'id_prospecto': prospecto.id
                }

                cur.execute(query, params)
                id_proceso_comercial: int = cur.fetchone()['id']

                query = '''
                    insert into EvaluacionRiesgo(rut_ej_comercial, id_proceso_comercial)
                    values (%(rut_ej_comercial)s, %(id_proceso_comercial)s)
                '''
                params = {
                    'rut_ej_comercial': prospecto.evaluacion_riesgo.ej_comercial.rut,
                    'id_proceso_comercial': id_proceso_comercial
                }

                cur.execute(query, params)

    def asignar_ejecutivo_evaluacion_proyectos(self, prospecto: Prospecto) -> None:
        if prospecto.id is None or prospecto.evaluacion_riesgo is None or prospecto.evaluacion_riesgo.ej_evaluacion is None:
            return
        
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select id
                    from ProcesoComercial
                    where id_prospecto = %(id_prospecto)s
                '''
                params = {
                    'id_prospecto': prospecto.id
                }

                cur.execute(query, params)
                id_proceso_comercial: int = cur.fetchone()['id']

                query = '''
                    update EvaluacionRiesgo
                    set rut_ej_evaluacion = %(rut_ej_evaluacion)s
                    where id_proceso_comercial = %(id_proceso_comercial)s
                '''
                params = {
                    'rut_ej_evaluacion': prospecto.evaluacion_riesgo.ej_evaluacion.rut,
                    'id_proceso_comercial': id_proceso_comercial
                }

                cur.execute(query, params)

    def cambiar_siguiente_estado(self, id: int) -> None:
        pass

    def __obtener_prospecto_condominio(self, id: int, cursor: Cursor[TupleRow]) -> ProspectoCondominio | None:
        query = '''
            select P.id as id_prospecto,
            P.rut_riesgo, P.nombre_riesgo,
            P.telefono_contacto, P.direccion,
            P.nombre_contacto, PCO.cargo_contacto,
            P.correo_contacto, P.observaciones,
            LN.nombre as linea_negocio,
            P.rut_registrado_por, U.nombre as nombre_registrado_por,
            C.nombre as comuna,
            PCO.tiene_locales_comerciales,
            PCO.uso_del_condominio,
            PCO.numero_pisos, PCO.numero_torres,
            PCO.cantidad_departamentos, 
            PCO.cantidad_subterraneos, PCO.tiene_piscina,
            PCO.year_construccion, PCO.metros_cuadrados,
            PCO.desea_ser_contactado,
            ER.id as id_evaluacion,
            ER.rut_ej_evaluacion, U_EJ_EV.nombre as nombre_ej_evaluacion,
            ER.rut_ej_comercial, U_EJ_COM.nombre as nombre_ej_comercial,
            ER.observaciones as observaciones_evaluacion,
            EB.nombre as nombre_estado,
            EB.codigo as codigo_estado,
            HE.fecha_registro as fecha_registro_estado,
            EP.dias_limite_particular, 
            EB.dias_limite as dias_limite_base,
            EB.codigo_siguiente_estado,
            EB2.nombre as nombre_siguiente_estado,
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
            left join EstadoBase EB2
            on EB.codigo_siguiente_estado = EB2.codigo
            left join EvaluacionRiesgo ER
            on PC.id = ER.id_proceso_comercial
            inner join Comuna C
            on P.id_comuna = C.id
            inner join Usuario U
            on P.rut_registrado_por = U.rut
            left join Usuario U_EJ_COM
            on ER.rut_ej_comercial = U_EJ_COM.rut
            left join Usuario U_EJ_EV
            on ER.rut_ej_evaluacion = U_EJ_EV.rut
            inner join LineaNegocio LN
            on P.id_linea_negocio = LN.id
            where P.id = %(id)s
        '''

        params = {
            'id': id
        }

        cursor.execute(query, params)
        rows = cursor.fetchall()

        if rows is None or len(rows) == 0:
            return None

        return TupleRowsProspectoCondominioAdapter(rows).to_prospecto_condominio()