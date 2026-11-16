from datetime import date

MESES_ES: dict[int, str] = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}


def resolver_periodo(
    mes: int | None, year: int | None
) -> tuple[int, int]:
    """Devuelve (year, mes) del período consultado.

    Cuando no se informan, se usa el mes y año en curso.
    """
    hoy = date.today()
    anio = year if year is not None else hoy.year
    mes_val = mes if mes is not None else hoy.month
    return anio, mes_val


def etiqueta_mes(year: int, mes: int) -> str:
    return f"{MESES_ES[mes]} {year}"


def mes_anterior(year: int, mes: int) -> tuple[int, int]:
    mes_ant = mes - 1 if mes > 1 else 12
    anio_ant = year if mes > 1 else year - 1
    return anio_ant, mes_ant
