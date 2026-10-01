from app.infraestructura.auditoria.descripciones.modelo import (
    AccionDescrita,
    EntidadAuditada,
    FragmentoFrase,
)


def formatear_entidad(entidad: EntidadAuditada) -> str:
    partes = []
    if entidad.etiqueta:
        partes.append(entidad.etiqueta)
    if entidad.nombre:
        partes.append(
            f"'{entidad.nombre}'" if entidad.entrecomillado else entidad.nombre
        )
    if entidad.identificador is not None:
        partes.append(f'({entidad.identificador})')

    texto = ' '.join(partes)
    if entidad.propietario is not None:
        texto = f'{texto} {formatear_propietario(entidad.propietario)}'
    return texto


def formatear_propietario(propietario: EntidadAuditada) -> str:
    contenido = formatear_entidad(propietario)
    if contenido.startswith('el '):
        return f'del {contenido[3:]}'
    return f'de {contenido}'


def formatear_fragmento(fragmento: FragmentoFrase) -> str:
    contenido = (
        formatear_entidad(fragmento.entidad)
        if fragmento.entidad is not None
        else fragmento.texto or ''
    )
    if not contenido:
        return ''
    if fragmento.preposicion:
        return f'{fragmento.preposicion} {contenido}'
    return contenido


def formatear_accion(actor: str | None, accion: AccionDescrita) -> str:
    actor = actor or 'desconocido'
    partes = [f'El usuario {actor} ha {accion.verbo}']

    for fragmento in accion.fragmentos:
        texto = formatear_fragmento(fragmento)
        if texto:
            partes.append(texto)

    frase = ' '.join(partes)
    if accion.sufijo:
        frase += accion.sufijo
    return frase
