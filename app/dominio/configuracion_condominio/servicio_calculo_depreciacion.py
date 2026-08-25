from datetime import datetime, timezone

from app.dominio.configuracion_condominio.parametros_depreciacion import ParametrosDepreciacion


class ServicioCalculoDepreciacion:

    @staticmethod
    def calcular(year_construccion: int, params: ParametrosDepreciacion) -> float:
        year_actual = datetime.now(tz=timezone.utc).year
        antiguedad = year_actual - year_construccion

        if antiguedad < params.antiguedad_sin_depreciacion:
            return 0.0

        if antiguedad >= params.antiguedad_maxima:
            return params.porcentaje_maximo / 100.0

        porcentaje = antiguedad * params.porcentaje_por_anio
        return min(porcentaje, params.porcentaje_maximo) / 100.0
