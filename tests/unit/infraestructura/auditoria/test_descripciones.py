from unittest.mock import MagicMock

import pytest

from app.dominio.auditoria.eventos_auditoria import EventoAuditoria
from app.infraestructura.auditoria.descripciones.construir_descripcion import (
    construir_descripcion_accion,
    descripcion_generica,
)
from app.infraestructura.auditoria.descripciones.resolvedor_nombres import (
    DatosOportunidad,
    ResolvedorNombres,
)


@pytest.fixture
def resolvedor():
    resolvedor = MagicMock(spec=ResolvedorNombres)
    resolvedor.nombre_prospecto.return_value = 'Torre Las Condes'
    resolvedor.nombre_cliente_por_id.return_value = 'Condominio El Roble'
    resolvedor.nombre_usuario.return_value = 'María López'
    resolvedor.nombre_contacto.return_value = 'Pedro Díaz'
    resolvedor.nombre_linea_negocio.return_value = 'Incendio'
    resolvedor.nombre_archivo.return_value = 'plano.pdf'
    resolvedor.nombre_company.return_value = 'Mapfre'
    resolvedor.nombre_producto.return_value = 'Incendio Total'
    resolvedor.nombre_administrador.return_value = 'Carlos Pérez'
    resolvedor.nombre_cliente_poliza.return_value = 'Jorge Maldonado Mena'
    resolvedor.datos_oportunidad.return_value = DatosOportunidad(
        producto='Seguro Hogar',
        cliente='Jorge Maldonado Mena',
        id_prospecto=680,
    )
    return resolvedor


def _construir(metodo, ruta, body, resolvedor, actor='19995707-4', evento_heuristico=EventoAuditoria.EJECUTAR_ACCION):
    return construir_descripcion_accion(
        metodo=metodo,
        ruta=ruta,
        evento_heuristico=evento_heuristico,
        actor=actor,
        body=body,
        resolvedor=resolvedor,
    )


@pytest.mark.unit
class TestEventoSemanticoPorRuta:

    def test_crear_poliza_en_oportunidad_es_crear(self, resolvedor):
        evento, _ = _construir(
            'POST', '/procesos-comerciales/442/polizas', {'numero_poliza': 'H-002'}, resolvedor,
        )

        assert evento == EventoAuditoria.CREAR

    def test_asignar_ejecutivo_es_accion(self, resolvedor):
        evento, _ = _construir(
            'POST', '/prospectos/680/asignar-ej-evaluacion', {'rut_ej_evaluacion': '12356487-1'}, resolvedor,
        )

        assert evento == EventoAuditoria.EJECUTAR_ACCION

    def test_registrar_contacto_es_crear(self, resolvedor):
        evento, _ = _construir(
            'POST', '/prospectos/5/contactos', {'nombre': 'Pedro Díaz'}, resolvedor,
        )

        assert evento == EventoAuditoria.CREAR

    def test_crear_plan_pago_es_crear(self, resolvedor):
        evento, _ = _construir(
            'POST', '/polizas/H-002/plan-pago', {'numero_cuotas': 12}, resolvedor,
        )

        assert evento == EventoAuditoria.CREAR

    def test_actualizar_es_actualizar(self, resolvedor):
        evento, _ = _construir(
            'PUT', '/prospectos/5', {'nombre_riesgo': 'Torre'}, resolvedor,
        )

        assert evento == EventoAuditoria.ACTUALIZAR

    def test_eliminar_es_eliminar(self, resolvedor):
        evento, _ = _construir('DELETE', '/contactos/3', None, resolvedor)

        assert evento == EventoAuditoria.ELIMINAR

    def test_completar_recordatorio_es_accion(self, resolvedor):
        evento, _ = _construir(
            'PATCH', '/recordatorios/9/completar', None, resolvedor,
        )

        assert evento == EventoAuditoria.EJECUTAR_ACCION

    def test_ruta_no_registrada_usa_evento_heuristico(self, resolvedor):
        evento, _ = _construir(
            'POST', '/recurso-desconocido/1/algo', None, resolvedor,
            evento_heuristico=EventoAuditoria.EJECUTAR_ACCION,
        )

        assert evento == EventoAuditoria.EJECUTAR_ACCION


@pytest.mark.unit
class TestFrasesDeAccion:

    def test_registrar_poliza_con_producto_y_cliente(self, resolvedor):
        _, descripcion = _construir(
            'POST', '/procesos-comerciales/442/polizas', {'numero_poliza': 'H-002'}, resolvedor,
        )

        assert descripcion == (
            "El usuario 19995707-4 ha registrado la póliza H-002 en la oportunidad "
            "'Seguro Hogar' (442) de Jorge Maldonado Mena (680)"
        )

    def test_probabilidad_de_cierre_con_porcentaje(self, resolvedor):
        _, descripcion = _construir(
            'PATCH',
            '/procesos-comerciales/441/probabilidad-cierre-ejecutivo',
            {'probabilidad_cierre_ejecutivo': 0.9},
            resolvedor,
        )

        assert descripcion == (
            "El usuario 19995707-4 ha asignado un 90% de probabilidad de cierre "
            "en la oportunidad 'Seguro Hogar' (441) de Jorge Maldonado Mena (680)"
        )

    def test_quitar_probabilidad_de_cierre(self, resolvedor):
        _, descripcion = _construir(
            'PATCH',
            '/procesos-comerciales/441/probabilidad-cierre-ejecutivo',
            {'probabilidad_cierre_ejecutivo': None},
            resolvedor,
        )

        assert 'ha quitado la probabilidad de cierre' in descripcion

    def test_asignar_ejecutivo_comercial(self, resolvedor):
        _, descripcion = _construir(
            'POST',
            '/prospectos/5/asignar-ej-comercial',
            {'rut_ej_comercial': '12356487-1'},
            resolvedor,
        )

        assert descripcion == (
            'El usuario 19995707-4 ha asignado la gestión comercial del prospecto '
            'Torre Las Condes (5) al usuario María López (12356487-1)'
        )

    def test_desasignar_ejecutivo_comercial(self, resolvedor):
        _, descripcion = _construir(
            'POST',
            '/prospectos/5/asignar-ej-comercial',
            {'rut_ej_comercial': None},
            resolvedor,
        )

        assert descripcion == (
            'El usuario 19995707-4 ha desasignado la gestión comercial del prospecto '
            'Torre Las Condes (5)'
        )

    def test_nombres_no_resueltos_usan_ids(self, resolvedor):
        resolvedor.nombre_prospecto.return_value = None
        resolvedor.nombre_usuario.return_value = None

        _, descripcion = _construir(
            'POST',
            '/prospectos/5/asignar-ej-comercial',
            {'rut_ej_comercial': '12356487-1'},
            resolvedor,
        )

        assert descripcion == (
            'El usuario 19995707-4 ha asignado la gestión comercial del prospecto '
            '(5) al usuario 12356487-1'
        )

    def test_cerrar_oportunidad_ganada(self, resolvedor):
        _, descripcion = _construir(
            'POST', '/procesos-comerciales/441/cerrar', {'ganado': True}, resolvedor,
        )

        assert descripcion == (
            "El usuario 19995707-4 ha cerrado como ganada la oportunidad "
            "'Seguro Hogar' (441) de Jorge Maldonado Mena (680)"
        )

    def test_registrar_prospecto_con_nombre_del_body(self, resolvedor):
        _, descripcion = _construir(
            'POST', '/prospectos/', {'nombre_riesgo': 'Torre Las Condes'}, resolvedor,
        )

        assert descripcion == 'El usuario 19995707-4 ha registrado el prospecto Torre Las Condes'

    def test_registrar_prospecto_sin_body(self, resolvedor):
        _, descripcion = _construir('POST', '/prospectos/', None, resolvedor)

        assert descripcion == 'El usuario 19995707-4 ha registrado un nuevo prospecto'

    def test_gestion_comercial_con_titulo(self, resolvedor):
        _, descripcion = _construir(
            'POST',
            '/gestiones-comerciales/',
            {'tipo': 'llamada', 'id_prospecto': 5, 'titulo': 'Llamada de seguimiento'},
            resolvedor,
        )

        assert descripcion == (
            'El usuario 19995707-4 ha registrado una gestión (llamada) '
            'en el prospecto Torre Las Condes (5): Llamada de seguimiento'
        )

    def test_plan_pago_con_cuotas(self, resolvedor):
        _, descripcion = _construir(
            'POST', '/polizas/H-002/plan-pago', {'numero_cuotas': 12}, resolvedor,
        )

        assert descripcion == (
            'El usuario 19995707-4 ha creado el plan de pago de la póliza '
            'H-002 de Jorge Maldonado Mena (12 cuotas)'
        )

    def test_cancelar_poliza(self, resolvedor):
        _, descripcion = _construir('POST', '/polizas/H-002/cancelar', None, resolvedor)

        assert descripcion == (
            'El usuario 19995707-4 ha cancelado la póliza H-002 de Jorge Maldonado Mena'
        )

    def test_fecha_estimada_cierre(self, resolvedor):
        _, descripcion = _construir(
            'PATCH',
            '/procesos-comerciales/441/fecha-estimada-cierre',
            {'fecha_estimada_cierre': '2026-12-15T00:00:00'},
            resolvedor,
        )

        assert descripcion == (
            "El usuario 19995707-4 ha fijado la fecha estimada de cierre en la "
            "oportunidad 'Seguro Hogar' (441) de Jorge Maldonado Mena (680) para el 2026-12-15"
        )

    def test_registrar_usuario(self, resolvedor):
        _, descripcion = _construir(
            'POST', '/usuarios/', {'rut': '12356487-1', 'nombre': 'María López'}, resolvedor,
        )

        assert descripcion == 'El usuario 19995707-4 ha registrado al usuario María López (12356487-1)'

    def test_pagar_cuota(self, resolvedor):
        _, descripcion = _construir('POST', '/cuota/77/pagar', None, resolvedor)

        assert descripcion == 'El usuario 19995707-4 ha registrado el pago de la cuota (77)'

    def test_marcar_notificacion_leida(self, resolvedor):
        _, descripcion = _construir('PATCH', '/notificaciones/15/leer', None, resolvedor)

        assert descripcion == 'El usuario 19995707-4 ha marcado como leída la notificación (15)'


@pytest.mark.unit
class TestFallbackGenerico:

    def test_ruta_sin_plantilla(self, resolvedor):
        _, descripcion = _construir('PATCH', '/recordatorios/99/completar-x', None, resolvedor)

        assert descripcion == 'El usuario 19995707-4 ha ejecutado PATCH /recordatorios/99/completar-x'

    def test_error_en_descriptor_cae_al_generico(self, resolvedor):
        resolvedor.datos_oportunidad.side_effect = RuntimeError('db caida')

        evento, descripcion = _construir(
            'POST', '/procesos-comerciales/442/polizas', {'numero_poliza': 'H-002'}, resolvedor,
            evento_heuristico=EventoAuditoria.EJECUTAR_ACCION,
        )

        assert evento == EventoAuditoria.EJECUTAR_ACCION
        assert descripcion == (
            'El usuario 19995707-4 ha ejecutado POST /procesos-comerciales/442/polizas'
        )

    def test_descripcion_generica_por_evento(self):
        assert descripcion_generica(
            EventoAuditoria.CREAR, 'POST', '/recordatorios/', '12345678-9',
        ) == 'El usuario 12345678-9 ha creado un registro en recordatorios'

        assert descripcion_generica(
            EventoAuditoria.ACTUALIZAR, 'PUT', '/companies-seguros/3', '12345678-9',
        ) == 'El usuario 12345678-9 ha actualizado companies-seguros (3)'

        assert descripcion_generica(
            EventoAuditoria.ELIMINAR, 'DELETE', '/companies-seguros/3', '12345678-9',
        ) == 'El usuario 12345678-9 ha eliminado companies-seguros (3)'

    def test_actor_desconocido(self, resolvedor):
        _, descripcion = _construir(
            'POST', '/prospectos/5/asignar-ej-comercial', {'rut_ej_comercial': None},
            resolvedor, actor=None,
        )

        assert descripcion.startswith('El usuario desconocido ha desasignado')
