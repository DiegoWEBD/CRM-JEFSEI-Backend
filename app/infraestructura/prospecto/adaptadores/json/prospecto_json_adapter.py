from app.dominio.prospecto.prospecto import Prospecto
from app.infraestructura.historial_estado.adaptadores.historial_estado_json_adapter import HistorialEstadoJsonAdapter
from app.infraestructura.usuario.adaptadores.usuario_json_resumen_adapter import UsuarioJsonResumenAdapter
from app.presentacion.api.prospecto.dto.prospecto_json import ProspectoJson


class ProspectoJsonAdapter:

    def __init__(self, prospecto: Prospecto):
        self.prospecto = prospecto

    def to_prospecto_json(self) -> ProspectoJson:
        return ProspectoJson(
            rut_riesgo=self.prospecto.rut_riesgo,
            nombre_riesgo=self.prospecto.nombre_riesgo,
            nombre_contacto=self.prospecto.nombre_contacto,
            telefono_contacto=self.prospecto.telefono_contacto,
            correo_contacto=self.prospecto.correo_contacto,
            direccion=self.prospecto.direccion,
            comuna=self.prospecto.comuna.nombre,
            historial_estados=[HistorialEstadoJsonAdapter(estado).to_historial_estado_json() for estado in self.prospecto.historial_estados],
            observaciones=self.prospecto.observaciones,
            linea_negocio=self.prospecto.linea_negocio.nombre,
            registrado_por=UsuarioJsonResumenAdapter(self.prospecto.registrado_por).to_usuario_json_resumen(),
            companies_sugeridas=[company.nombre for company in self.prospecto.companies_sugeridas],
            id=self.prospecto.id
        )