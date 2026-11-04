import pytest

from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.dominio.prospecto.prospecto_empresa.servicio_giros_comerciales import ServicioGirosComerciales


@pytest.mark.unit
class TestClaveNormalizada:

    def test_ignora_mayusculas(self):
        assert ServicioGirosComerciales.clave_normalizada('Comercio') == ServicioGirosComerciales.clave_normalizada('comercio')

    def test_ignora_tildes(self):
        assert ServicioGirosComerciales.clave_normalizada('Molienda') == ServicioGirosComerciales.clave_normalizada('moliénda')

    def test_colapsa_espacios_y_bordes(self):
        assert ServicioGirosComerciales.clave_normalizada('  Comercio   General  ') == 'comercio general'

    def test_conserva_la_puntuacion(self):
        assert ServicioGirosComerciales.clave_normalizada('S.A.') == 's.a.'


@pytest.mark.unit
class TestEsElMismoGiro:

    def test_nombres_equivalentes_son_el_mismo_giro(self):
        assert ServicioGirosComerciales.es_el_mismo_giro('Comercio', 'comercio') is True

    def test_nombres_distintos_no_son_el_mismo_giro(self):
        assert ServicioGirosComerciales.es_el_mismo_giro('Comercio', 'Minería') is False


@pytest.mark.unit
class TestValidarNombres:

    def test_acepta_nombres_distintos(self):
        ServicioGirosComerciales.validar_nombres(['Comercio', 'Minería'])

    def test_acepta_lista_vacia(self):
        ServicioGirosComerciales.validar_nombres([])

    def test_rechaza_nombre_vacio(self):
        with pytest.raises(ConflictoEnAccionException):
            ServicioGirosComerciales.validar_nombres(['   '])

    def test_rechaza_nombres_repetidos(self):
        with pytest.raises(RecursoYaExisteException):
            ServicioGirosComerciales.validar_nombres(['Comercio', 'Comercio'])

    def test_rechaza_repetidos_ignorando_mayusculas_y_tildes(self):
        with pytest.raises(RecursoYaExisteException):
            ServicioGirosComerciales.validar_nombres(['Molienda', 'moliénda'])
