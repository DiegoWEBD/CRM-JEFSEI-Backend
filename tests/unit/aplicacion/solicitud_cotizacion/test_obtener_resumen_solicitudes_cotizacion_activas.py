from unittest.mock import MagicMock

import pytest

from app.aplicacion.solicitud_cotizacion.dto.contadores_solicitudes_cotizacion import (
    ContadoresSolicitudesCotizacion,
)
from app.aplicacion.solicitud_cotizacion.dto.filtro_solicitudes_cotizacion import (
    FiltroSolicitudesCotizacion,
)
from app.aplicacion.solicitud_cotizacion.dto.solicitud_cotizacion_resumen import (
    SolicitudCotizacionResumen,
)
from app.aplicacion.solicitud_cotizacion.servicios.consulta_solicitudes_cotizacion_service import (
    ConsultaSolicitudesCotizacionService,
)
from app.aplicacion.solicitud_cotizacion.use_cases.obtener_resumen_solicitudes_cotizacion_activas import (
    ObtenerResumenSolicitudesCotizacionActivasUseCase,
)
from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos


def _resumen(id_solicitud: int, id_prospecto: int = 10) -> SolicitudCotizacionResumen:
    return SolicitudCotizacionResumen(
        id=id_solicitud,
        id_prospecto=id_prospecto,
        nombre_riesgo=f'Riesgo {id_solicitud}',
        informacion_completa=True,
        ejecutivo_comercial='Ana Pérez',
        tipo='incendio',
        recotizacion=False,
        motivo_recotizacion=None,
        producto='Incendio Condominio',
        prioridad='alta',
        fecha='2026-11-10T10:00:00',
        tiene_cotizaciones=False,
        campos_faltantes=[],
        estudio_disponible=False,
    )


def _prospecto_mock(id_prospecto: int = 10):
    prospecto = MagicMock()
    prospecto.id = id_prospecto
    prospecto.linea_negocio.nombre = 'Incendio'
    prospecto.rut_riesgo = '76.123.456-7'
    prospecto.telefono_contacto = '+56912345678'
    prospecto.correo_contacto = 'contacto@correo.cl'
    prospecto.direccion = 'Av. Uno 123'
    prospecto.region = 'Metropolitana'
    prospecto.comuna = 'Santiago'
    return prospecto


CONTADORES = ContadoresSolicitudesCotizacion(
    informacion_incompleta=1,
    listas_para_cotizar=2,
    cotizaciones_emitidas=3,
    estudios_emitidos=4,
)


@pytest.mark.unit
class TestObtenerResumenSolicitudesCotizacion:

    def _use_case(self, filas=None, total=0, contadores=None):
        consulta_service = MagicMock(spec=ConsultaSolicitudesCotizacionService)
        consulta_service.listar.return_value = (filas if filas is not None else [], total)
        consulta_service.contadores.return_value = contadores or CONTADORES

        repositorio_prospectos = MagicMock(spec=RepositorioProspectos)
        repositorio_prospectos.buscar.return_value = _prospecto_mock()

        use_case = ObtenerResumenSolicitudesCotizacionActivasUseCase(
            consulta_service=consulta_service,
            repositorio_prospectos=repositorio_prospectos,
        )
        return use_case, consulta_service, repositorio_prospectos

    def test_devuelve_listado_con_total_y_contadores_propagados(self):
        filas = [_resumen(1), _resumen(2)]
        use_case, consulta_service, _ = self._use_case(filas=filas, total=23)

        filtro = FiltroSolicitudesCotizacion(pagina=2, tamano_pagina=5)
        listado = use_case.ejecutar('11111111-1', filtro)

        assert listado.solicitudes == filas
        assert listado.total == 23
        assert listado.contadores == CONTADORES

        consulta_service.listar.assert_called_once()
        rut_scoping, filtro_recibido = consulta_service.listar.call_args.args
        assert rut_scoping == '11111111-1'
        assert filtro_recibido.pagina == 2
        assert filtro_recibido.tamano_pagina == 5
        consulta_service.contadores.assert_called_once_with('11111111-1')

    def test_campos_faltantes_solo_sobre_las_filas_de_la_pagina(self):
        filas = [_resumen(1), _resumen(2)]
        use_case, _, repositorio_prospectos = self._use_case(filas=filas, total=500)

        listado = use_case.ejecutar(None, FiltroSolicitudesCotizacion())

        assert repositorio_prospectos.buscar.call_count == 2
        assert all(s.campos_faltantes == [] for s in listado.solicitudes)

    def test_estado_invalido_lanza_dato_invalido(self):
        use_case, consulta_service, _ = self._use_case()

        with pytest.raises(DatoInvalidoException):
            use_case.ejecutar(None, FiltroSolicitudesCotizacion(estado='lo_que_sea'))

        consulta_service.listar.assert_not_called()

    def test_prioridad_invalida_lanza_dato_invalido(self):
        use_case, consulta_service, _ = self._use_case()

        with pytest.raises(DatoInvalidoException):
            use_case.ejecutar(None, FiltroSolicitudesCotizacion(prioridad='media'))

        consulta_service.listar.assert_not_called()

    def test_normaliza_texto_busqueda_y_valores_vacios(self):
        use_case, consulta_service, _ = self._use_case()

        use_case.ejecutar(
            None,
            FiltroSolicitudesCotizacion(
                texto_busqueda='  cotiza  ',
                estado='',
                prioridad='',
                rut_usuario='',
            ),
        )

        filtro_recibido = consulta_service.listar.call_args.args[1]
        assert filtro_recibido.texto_busqueda == 'cotiza'
        assert filtro_recibido.estado is None
        assert filtro_recibido.prioridad is None
        assert filtro_recibido.rut_usuario is None

    def test_normaliza_texto_busqueda_solo_espacios_a_none(self):
        use_case, consulta_service, _ = self._use_case()

        use_case.ejecutar(None, FiltroSolicitudesCotizacion(texto_busqueda='   '))

        filtro_recibido = consulta_service.listar.call_args.args[1]
        assert filtro_recibido.texto_busqueda is None

    def test_prospecto_no_encontrado_lanza_recurso_no_encontrado(self):
        use_case, _, repositorio_prospectos = self._use_case(filas=[_resumen(1)])
        repositorio_prospectos.buscar.return_value = None

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(None, FiltroSolicitudesCotizacion())
