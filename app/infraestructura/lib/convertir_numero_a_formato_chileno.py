def convertir_numero_a_formato_chileno(numero: int | float) -> str:
    numero_formateado = f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    partes = numero_formateado.split(',')

    if len(partes) != 2:
        return numero_formateado
    
    decimales = int(partes[1])
    entero = partes[0]

    if decimales == 0:
        return entero.strip()
    
    return numero_formateado.strip()