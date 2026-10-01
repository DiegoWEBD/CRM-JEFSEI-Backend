import re
from dataclasses import dataclass

from app.dominio.auditoria.eventos_auditoria import EventoAuditoria
from app.infraestructura.auditoria.descripciones.modelo import (
    AccionDescrita,
    EntidadAuditada,
    FragmentoFrase,
)
from app.infraestructura.auditoria.descripciones.resolvedor_nombres import ResolvedorNombres


@dataclass
class EntradaAccion:
    metodo: str
    patron: re.Pattern
    evento: str
    descriptor: object


def _prospecto(id_prospecto: int, resolvedor: ResolvedorNombres, articulo: str = 'el prospecto') -> EntidadAuditada:
    return EntidadAuditada(
        etiqueta=articulo,
        nombre=resolvedor.nombre_prospecto(id_prospecto),
        identificador=id_prospecto,
    )


def _cliente(id_cliente: int, resolvedor: ResolvedorNombres, articulo: str = 'el cliente') -> EntidadAuditada:
    return EntidadAuditada(
        etiqueta=articulo,
        nombre=resolvedor.nombre_cliente_por_id(id_cliente),
        identificador=id_cliente,
    )


def _oportunidad(id_proceso: int, resolvedor: ResolvedorNombres) -> EntidadAuditada:
    datos = resolvedor.datos_oportunidad(id_proceso)
    propietario = None
    if datos is not None and (datos.cliente or datos.id_prospecto is not None):
        propietario = EntidadAuditada(
            etiqueta='',
            nombre=datos.cliente,
            identificador=datos.id_prospecto,
        )
    return EntidadAuditada(
        etiqueta='la oportunidad',
        nombre=datos.producto if datos is not None else None,
        identificador=id_proceso,
        propietario=propietario,
        entrecomillado=True,
    )


def _poliza(numero_poliza: str, resolvedor: ResolvedorNombres) -> EntidadAuditada:
    propietario = None
    cliente = resolvedor.nombre_cliente_poliza(numero_poliza)
    if cliente:
        propietario = EntidadAuditada(etiqueta='', nombre=cliente)
    return EntidadAuditada(
        etiqueta='la póliza',
        nombre=numero_poliza,
        propietario=propietario,
    )


def _usuario_con_datos(nombre: str | None, rut: str | None, articulo: str) -> EntidadAuditada:
    if nombre:
        return EntidadAuditada(etiqueta=articulo, nombre=nombre, identificador=rut)
    # Sin nombre resuelto el RUT se muestra directo (código legible, no id surrogate)
    return EntidadAuditada(etiqueta=articulo, nombre=rut)


def _usuario(rut: str, resolvedor: ResolvedorNombres, articulo: str = 'el usuario') -> EntidadAuditada:
    return _usuario_con_datos(resolvedor.nombre_usuario(rut), rut, articulo)


def _destino_usuario(rut: str | None, resolvedor: ResolvedorNombres) -> FragmentoFrase | None:
    if not rut:
        return None
    return FragmentoFrase(preposicion='al', entidad=_usuario(rut, resolvedor, articulo='usuario'))


def _asignacion(papel: str, destino: EntidadAuditada, rut_destino: str | None, resolvedor: ResolvedorNombres) -> AccionDescrita:
    fragmentos = [FragmentoFrase(entidad=EntidadAuditada(etiqueta=papel, propietario=destino))]
    fragmento_destino = _destino_usuario(rut_destino, resolvedor)
    if fragmento_destino:
        fragmentos.append(fragmento_destino)
    return AccionDescrita(
        evento=EventoAuditoria.EJECUTAR_ACCION,
        verbo='asignado' if rut_destino else 'desasignado',
        fragmentos=fragmentos,
    )


def _porcentaje(valor: float) -> str:
    return f'{round(valor * 100):g}'


# ---------------------------------------------------------------------------
# Prospectos
# ---------------------------------------------------------------------------

def _registrar_prospecto(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    nombre = body.get('nombre_riesgo')
    if nombre:
        return AccionDescrita(
            evento=EventoAuditoria.CREAR,
            verbo='registrado',
            fragmentos=[FragmentoFrase(entidad=EntidadAuditada(etiqueta='el prospecto', nombre=nombre))],
        )
    return AccionDescrita(
        evento=EventoAuditoria.CREAR,
        verbo='registrado',
        fragmentos=[FragmentoFrase(texto='un nuevo prospecto')],
    )


def _asignar_ej_comercial(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return _asignacion(
        'la gestión comercial',
        _prospecto(int(params['id']), resolvedor),
        body.get('rut_ej_comercial'),
        resolvedor,
    )


def _asignar_ej_evaluacion(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return _asignacion(
        'la evaluación de proyectos',
        _prospecto(int(params['id']), resolvedor),
        body.get('rut_ej_evaluacion'),
        resolvedor,
    )


def _asignar_ej_cobranza(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return _asignacion(
        'la cobranza',
        _cliente(int(params['id']), resolvedor),
        body.get('rut_ej_cobranza'),
        resolvedor,
    )


def _asignar_ej_renovacion(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return _asignacion(
        'la renovación',
        _cliente(int(params['id']), resolvedor),
        body.get('rut_ej_renovacion'),
        resolvedor,
    )


def _actualizar_prospecto(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.ACTUALIZAR,
        verbo='actualizado',
        fragmentos=[FragmentoFrase(entidad=_prospecto(int(params['id']), resolvedor))],
    )


def _cambiar_linea_negocio(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    fragmentos = [
        FragmentoFrase(
            preposicion='del',
            entidad=_prospecto(int(params['id']), resolvedor, articulo='prospecto'),
        )
    ]
    id_linea = body.get('id_linea_negocio')
    if id_linea is not None:
        fragmentos.append(FragmentoFrase(
            preposicion='a',
            entidad=EntidadAuditada(
                etiqueta='la línea de negocio',
                nombre=resolvedor.nombre_linea_negocio(int(id_linea)),
                identificador=id_linea,
            ),
        ))
    return AccionDescrita(
        evento=EventoAuditoria.ACTUALIZAR,
        verbo='cambiado la línea de negocio',
        fragmentos=fragmentos,
    )


def _actualizar_ficha_condominio(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.ACTUALIZAR,
        verbo='actualizado la ficha de condominio',
        fragmentos=[FragmentoFrase(
            preposicion='del',
            entidad=_prospecto(int(params['id']), resolvedor, articulo='prospecto'),
        )],
    )


def _fijar_valor_uf_m2(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    valor = body.get('valor_uf_m2_personalizado')
    verbo = (
        'quitado el valor UF/m² personalizado'
        if valor is None
        else f'fijado un valor UF/m² personalizado de {float(valor):g}'
    )
    return AccionDescrita(
        evento=EventoAuditoria.EJECUTAR_ACCION,
        verbo=verbo,
        fragmentos=[FragmentoFrase(entidad=_prospecto(int(params['id']), resolvedor))],
    )


def _registrar_contacto(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.CREAR,
        verbo='registrado',
        fragmentos=[
            FragmentoFrase(entidad=EntidadAuditada(etiqueta='el contacto', nombre=body.get('nombre'))),
            FragmentoFrase(preposicion='en', entidad=_prospecto(int(params['id']), resolvedor)),
        ],
    )


def _actualizar_contacto(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.ACTUALIZAR,
        verbo='actualizado',
        fragmentos=[FragmentoFrase(entidad=EntidadAuditada(
            etiqueta='el contacto',
            nombre=resolvedor.nombre_contacto(int(params['id'])),
            identificador=params['id'],
        ))],
    )


def _eliminar_contacto(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.ELIMINAR,
        verbo='eliminado',
        fragmentos=[FragmentoFrase(entidad=EntidadAuditada(
            etiqueta='el contacto',
            nombre=resolvedor.nombre_contacto(int(params['id'])),
            identificador=params['id'],
        ))],
    )


def _subir_archivo(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.CREAR,
        verbo='subido un archivo',
        fragmentos=[FragmentoFrase(
            preposicion='al',
            entidad=_prospecto(int(params['id_prospecto']), resolvedor, articulo='prospecto'),
        )],
    )


def _eliminar_archivo(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.ELIMINAR,
        verbo='eliminado',
        fragmentos=[
            FragmentoFrase(entidad=EntidadAuditada(
                etiqueta='el archivo',
                nombre=resolvedor.nombre_archivo(int(params['id_archivo'])),
                identificador=params['id_archivo'],
            )),
            FragmentoFrase(
                preposicion='del',
                entidad=_prospecto(int(params['id_prospecto']), resolvedor, articulo='prospecto'),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Oportunidades (procesos comerciales)
# ---------------------------------------------------------------------------

def _crear_proceso_comercial(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    fragmentos = []
    id_prospecto = body.get('id_prospecto')
    if id_prospecto is not None:
        fragmentos.append(FragmentoFrase(
            preposicion='para',
            entidad=_prospecto(int(id_prospecto), resolvedor),
        ))
    return AccionDescrita(
        evento=EventoAuditoria.CREAR,
        verbo='creado una oportunidad comercial',
        fragmentos=fragmentos,
    )


def _cerrar_proceso_comercial(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    ganado = body.get('ganado')
    if ganado is True:
        verbo = 'cerrado como ganada'
    elif ganado is False:
        verbo = 'cerrado como perdida'
    else:
        verbo = 'cerrado'
    return AccionDescrita(
        evento=EventoAuditoria.EJECUTAR_ACCION,
        verbo=verbo,
        fragmentos=[FragmentoFrase(entidad=_oportunidad(int(params['id']), resolvedor))],
    )


def _aceptacion_proceso_comercial(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.EJECUTAR_ACCION,
        verbo='registrado la aceptación del cliente',
        fragmentos=[FragmentoFrase(preposicion='en', entidad=_oportunidad(int(params['id']), resolvedor))],
    )


def _fecha_estimada_cierre(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    fecha = body.get('fecha_estimada_cierre')
    fragmentos = [FragmentoFrase(preposicion='en', entidad=_oportunidad(int(params['id']), resolvedor))]
    if fecha:
        fragmentos.append(FragmentoFrase(texto=f'para el {str(fecha)[:10]}'))
    return AccionDescrita(
        evento=EventoAuditoria.ACTUALIZAR,
        verbo='fijado la fecha estimada de cierre',
        fragmentos=fragmentos,
    )


def _probabilidad_cierre(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    probabilidad = body.get('probabilidad_cierre_ejecutivo')
    fragmentos = []
    if probabilidad is None:
        verbo = 'quitado la probabilidad de cierre'
    else:
        verbo = 'asignado'
        fragmentos.append(FragmentoFrase(texto=f'un {_porcentaje(float(probabilidad))}% de probabilidad de cierre'))
    fragmentos.append(FragmentoFrase(preposicion='en', entidad=_oportunidad(int(params['id']), resolvedor)))
    return AccionDescrita(
        evento=EventoAuditoria.ACTUALIZAR,
        verbo=verbo,
        fragmentos=fragmentos,
    )


def _solicitar_cotizacion(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    tipo = body.get('tipo')
    return AccionDescrita(
        evento=EventoAuditoria.CREAR,
        verbo='registrado una solicitud de cotización',
        fragmentos=[FragmentoFrase(preposicion='para', entidad=_oportunidad(int(params['id']), resolvedor))],
        sufijo=f' (tipo: {tipo})' if tipo else None,
    )


def _solicitar_recotizacion(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.CREAR,
        verbo='registrado una recotización',
        fragmentos=[FragmentoFrase(preposicion='para', entidad=_oportunidad(int(params['id']), resolvedor))],
    )


def _registrar_poliza_en_oportunidad(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    numero_poliza = body.get('numero_poliza')
    poliza = (
        EntidadAuditada(etiqueta='la póliza', nombre=numero_poliza)
        if numero_poliza
        else EntidadAuditada(etiqueta='una póliza')
    )
    return AccionDescrita(
        evento=EventoAuditoria.CREAR,
        verbo='registrado',
        fragmentos=[
            FragmentoFrase(entidad=poliza),
            FragmentoFrase(preposicion='en', entidad=_oportunidad(int(params['id']), resolvedor)),
        ],
    )


# ---------------------------------------------------------------------------
# Pólizas, planes de pago y cuotas
# ---------------------------------------------------------------------------

def _registrar_renovacion_cotizada(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.EJECUTAR_ACCION,
        verbo='registrado la cotización de renovación',
        fragmentos=[FragmentoFrase(preposicion='de', entidad=_poliza(params['numero'], resolvedor))],
    )


def _crear_plan_pago(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    numero_cuotas = body.get('numero_cuotas')
    return AccionDescrita(
        evento=EventoAuditoria.CREAR,
        verbo='creado el plan de pago',
        fragmentos=[FragmentoFrase(preposicion='de', entidad=_poliza(params['numero'], resolvedor))],
        sufijo=f' ({numero_cuotas} cuotas)' if numero_cuotas is not None else None,
    )


def _cancelar_poliza(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.EJECUTAR_ACCION,
        verbo='cancelado',
        fragmentos=[FragmentoFrase(entidad=_poliza(params['numero'], resolvedor))],
    )


def _reactivar_poliza(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.EJECUTAR_ACCION,
        verbo='reactivado',
        fragmentos=[FragmentoFrase(entidad=_poliza(params['numero'], resolvedor))],
    )


def _actualizar_poliza(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.ACTUALIZAR,
        verbo='actualizado',
        fragmentos=[FragmentoFrase(entidad=_poliza(params['numero'], resolvedor))],
    )


def _pagar_cuota(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.EJECUTAR_ACCION,
        verbo='registrado el pago',
        fragmentos=[FragmentoFrase(
            preposicion='de',
            entidad=EntidadAuditada(etiqueta='la cuota', identificador=params['id']),
        )],
    )


# ---------------------------------------------------------------------------
# Solicitudes de cotización, estudios y gestiones comerciales
# ---------------------------------------------------------------------------

def _registrar_cotizacion(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.CREAR,
        verbo='registrado una cotización',
        fragmentos=[FragmentoFrase(preposicion='en', entidad=_solicitud(int(params['id'])))],
    )


def _subir_estudio_comercial(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.CREAR,
        verbo='subido un estudio comercial',
        fragmentos=[FragmentoFrase(preposicion='a', entidad=_solicitud(int(params['id'])))],
    )


def _generar_estudio_comercial(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    fragmentos = []
    id_prospecto = body.get('id_prospecto')
    if id_prospecto is not None:
        fragmentos.append(FragmentoFrase(
            preposicion='para',
            entidad=_prospecto(int(id_prospecto), resolvedor),
        ))
    return AccionDescrita(
        evento=EventoAuditoria.CREAR,
        verbo='generado un estudio comercial',
        fragmentos=fragmentos,
    )


def _registrar_gestion_comercial(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    tipo = body.get('tipo')
    fragmentos = [FragmentoFrase(texto=f'una gestión ({tipo})' if tipo else 'una gestión comercial')]
    id_prospecto = body.get('id_prospecto')
    if id_prospecto is not None:
        fragmentos.append(FragmentoFrase(
            preposicion='en',
            entidad=_prospecto(int(id_prospecto), resolvedor),
        ))
    titulo = body.get('titulo')
    return AccionDescrita(
        evento=EventoAuditoria.CREAR,
        verbo='registrado',
        fragmentos=fragmentos,
        sufijo=f': {titulo}' if titulo else None,
    )


# ---------------------------------------------------------------------------
# Usuarios, administradores, companies y productos
# ---------------------------------------------------------------------------

def _registrar_usuario(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.CREAR,
        verbo='registrado',
        fragmentos=[FragmentoFrase(
            preposicion='al',
            entidad=_usuario_con_datos(body.get('nombre'), body.get('rut'), 'usuario'),
        )],
    )


def _actualizar_usuario(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    rut = params['rut']
    return AccionDescrita(
        evento=EventoAuditoria.ACTUALIZAR,
        verbo='actualizado',
        fragmentos=[FragmentoFrase(
            preposicion='al',
            entidad=_usuario_con_datos(body.get('nombre') or resolvedor.nombre_usuario(rut), rut, 'usuario'),
        )],
    )


def _eliminar_usuario(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    rut = params['rut']
    return AccionDescrita(
        evento=EventoAuditoria.ELIMINAR,
        verbo='eliminado',
        fragmentos=[FragmentoFrase(
            preposicion='al',
            entidad=_usuario_con_datos(resolvedor.nombre_usuario(rut), rut, 'usuario'),
        )],
    )


def _registrar_administrador(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.CREAR,
        verbo='registrado',
        fragmentos=[FragmentoFrase(entidad=EntidadAuditada(
            etiqueta='el administrador de condominio',
            nombre=body.get('nombre_administrador'),
        ))],
    )


def _actualizar_administrador(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.ACTUALIZAR,
        verbo='actualizado',
        fragmentos=[FragmentoFrase(entidad=EntidadAuditada(
            etiqueta='el administrador de condominio',
            nombre=body.get('nombre_administrador') or resolvedor.nombre_administrador(int(params['id'])),
            identificador=params['id'],
        ))],
    )


def _crear_company(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.CREAR,
        verbo='registrado',
        fragmentos=[FragmentoFrase(entidad=EntidadAuditada(
            etiqueta='la compañía de seguros',
            nombre=body.get('nombre'),
        ))],
    )


def _actualizar_company(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    id_company = int(params['id'])
    return AccionDescrita(
        evento=EventoAuditoria.ACTUALIZAR,
        verbo='actualizado',
        fragmentos=[FragmentoFrase(entidad=EntidadAuditada(
            etiqueta='la compañía de seguros',
            nombre=body.get('nombre') or resolvedor.nombre_company(id_company),
            identificador=id_company,
        ))],
    )


def _eliminar_company(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    id_company = int(params['id'])
    return AccionDescrita(
        evento=EventoAuditoria.ELIMINAR,
        verbo='eliminado',
        fragmentos=[FragmentoFrase(entidad=EntidadAuditada(
            etiqueta='la compañía de seguros',
            nombre=resolvedor.nombre_company(id_company),
            identificador=id_company,
        ))],
    )


def _actualizar_factores_cuotas(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    id_company = int(params['id'])
    return AccionDescrita(
        evento=EventoAuditoria.EJECUTAR_ACCION,
        verbo='actualizado los factores de cuotas',
        fragmentos=[FragmentoFrase(preposicion='de', entidad=EntidadAuditada(
            etiqueta='la compañía de seguros',
            nombre=resolvedor.nombre_company(id_company),
            identificador=id_company,
        ))],
    )


def _crear_producto(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    id_linea = body.get('id_linea_negocio')
    fragmentos = [FragmentoFrase(entidad=EntidadAuditada(etiqueta='el producto', nombre=body.get('nombre')))]
    if id_linea is not None:
        fragmentos.append(FragmentoFrase(
            preposicion='en',
            entidad=EntidadAuditada(
                etiqueta='la línea de negocio',
                nombre=resolvedor.nombre_linea_negocio(int(id_linea)),
                identificador=id_linea,
            ),
        ))
    return AccionDescrita(evento=EventoAuditoria.CREAR, verbo='registrado', fragmentos=fragmentos)


def _actualizar_producto(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    id_producto = int(params['id'])
    return AccionDescrita(
        evento=EventoAuditoria.ACTUALIZAR,
        verbo='actualizado',
        fragmentos=[FragmentoFrase(entidad=EntidadAuditada(
            etiqueta='el producto',
            nombre=body.get('nombre') or resolvedor.nombre_producto(id_producto),
            identificador=id_producto,
        ))],
    )


def _eliminar_producto(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    id_producto = int(params['id'])
    return AccionDescrita(
        evento=EventoAuditoria.ELIMINAR,
        verbo='eliminado',
        fragmentos=[FragmentoFrase(entidad=EntidadAuditada(
            etiqueta='el producto',
            nombre=resolvedor.nombre_producto(id_producto),
            identificador=id_producto,
        ))],
    )


# ---------------------------------------------------------------------------
# Recordatorios, notificaciones, configuración y comunicados
# ---------------------------------------------------------------------------

def _registrar_recordatorio(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    fragmentos = [FragmentoFrase(entidad=EntidadAuditada(
        etiqueta='el recordatorio',
        nombre=body.get('titulo'),
    ))]
    id_prospecto = body.get('id_prospecto')
    if id_prospecto is not None:
        fragmentos.append(FragmentoFrase(
            preposicion='para',
            entidad=_prospecto(int(id_prospecto), resolvedor),
        ))
    return AccionDescrita(evento=EventoAuditoria.CREAR, verbo='registrado', fragmentos=fragmentos)


def _actualizar_recordatorio(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.ACTUALIZAR,
        verbo='actualizado',
        fragmentos=[FragmentoFrase(entidad=EntidadAuditada(
            etiqueta='el recordatorio',
            nombre=body.get('titulo'),
            identificador=params['id'],
        ))],
    )


def _completar_recordatorio(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.EJECUTAR_ACCION,
        verbo='marcado como completado',
        fragmentos=[FragmentoFrase(entidad=EntidadAuditada(
            etiqueta='el recordatorio',
            identificador=params['id'],
        ))],
    )


def _eliminar_recordatorio(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.ELIMINAR,
        verbo='eliminado',
        fragmentos=[FragmentoFrase(entidad=EntidadAuditada(
            etiqueta='el recordatorio',
            identificador=params['id'],
        ))],
    )


def _marcar_notificacion_leida(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.EJECUTAR_ACCION,
        verbo='marcado como leída',
        fragmentos=[FragmentoFrase(entidad=EntidadAuditada(
            etiqueta='la notificación',
            identificador=params['id'],
        ))],
    )


def _marcar_todas_notificaciones_leidas(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.EJECUTAR_ACCION,
        verbo='marcado como leídas todas sus notificaciones',
    )


def _guardar_valor_uf_region(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.ACTUALIZAR,
        verbo='guardado el valor UF/m²',
        fragmentos=[FragmentoFrase(preposicion='de', entidad=EntidadAuditada(
            etiqueta='la región',
            nombre=body.get('region'),
        ))],
    )


def _eliminar_valor_uf_region(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.ELIMINAR,
        verbo='eliminado el valor UF/m²',
        fragmentos=[FragmentoFrase(preposicion='de', entidad=EntidadAuditada(
            etiqueta='la región',
            identificador=params['id'],
        ))],
    )


def _guardar_parametros_depreciacion(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.ACTUALIZAR,
        verbo='guardado los parámetros de depreciación de condominios',
    )


def _publicar_comunicado(params: dict, body: dict, resolvedor: ResolvedorNombres) -> AccionDescrita:
    return AccionDescrita(
        evento=EventoAuditoria.CREAR,
        verbo='publicado',
        fragmentos=[FragmentoFrase(entidad=EntidadAuditada(
            etiqueta='el comunicado de gerencia',
            nombre=body.get('titulo'),
        ))],
    )


REGISTRO = [
    # Prospectos
    EntradaAccion('POST', re.compile(r'^/prospectos/?$'), EventoAuditoria.CREAR, _registrar_prospecto),
    EntradaAccion('POST', re.compile(r'^/prospectos/(?P<id>\d+)/asignar-ej-comercial$'), EventoAuditoria.EJECUTAR_ACCION, _asignar_ej_comercial),
    EntradaAccion('POST', re.compile(r'^/prospectos/(?P<id>\d+)/asignar-ej-evaluacion$'), EventoAuditoria.EJECUTAR_ACCION, _asignar_ej_evaluacion),
    EntradaAccion('PUT', re.compile(r'^/prospectos/(?P<id>\d+)$'), EventoAuditoria.ACTUALIZAR, _actualizar_prospecto),
    EntradaAccion('PATCH', re.compile(r'^/prospectos/(?P<id>\d+)/linea-negocio$'), EventoAuditoria.ACTUALIZAR, _cambiar_linea_negocio),
    EntradaAccion('PUT', re.compile(r'^/prospectos/condominios/(?P<id>\d+)$'), EventoAuditoria.ACTUALIZAR, _actualizar_ficha_condominio),
    EntradaAccion('PATCH', re.compile(r'^/prospectos/condominios/(?P<id>\d+)/valor-uf-m2-personalizado$'), EventoAuditoria.EJECUTAR_ACCION, _fijar_valor_uf_m2),
    EntradaAccion('POST', re.compile(r'^/prospectos/(?P<id>\d+)/contactos$'), EventoAuditoria.CREAR, _registrar_contacto),
    EntradaAccion('POST', re.compile(r'^/prospectos/(?P<id_prospecto>\d+)/archivos/?$'), EventoAuditoria.CREAR, _subir_archivo),
    EntradaAccion('DELETE', re.compile(r'^/prospectos/(?P<id_prospecto>\d+)/archivos/(?P<id_archivo>\d+)$'), EventoAuditoria.ELIMINAR, _eliminar_archivo),
    # Clientes
    EntradaAccion('POST', re.compile(r'^/clientes/(?P<id>\d+)/asignar-ej-cobranza$'), EventoAuditoria.EJECUTAR_ACCION, _asignar_ej_cobranza),
    EntradaAccion('POST', re.compile(r'^/clientes/(?P<id>\d+)/asignar-ej-renovacion$'), EventoAuditoria.EJECUTAR_ACCION, _asignar_ej_renovacion),
    # Contactos
    EntradaAccion('PUT', re.compile(r'^/contactos/(?P<id>\d+)$'), EventoAuditoria.ACTUALIZAR, _actualizar_contacto),
    EntradaAccion('DELETE', re.compile(r'^/contactos/(?P<id>\d+)$'), EventoAuditoria.ELIMINAR, _eliminar_contacto),
    # Oportunidades
    EntradaAccion('POST', re.compile(r'^/procesos-comerciales/?$'), EventoAuditoria.CREAR, _crear_proceso_comercial),
    EntradaAccion('POST', re.compile(r'^/procesos-comerciales/(?P<id>\d+)/cerrar$'), EventoAuditoria.EJECUTAR_ACCION, _cerrar_proceso_comercial),
    EntradaAccion('POST', re.compile(r'^/procesos-comerciales/(?P<id>\d+)/aceptacion$'), EventoAuditoria.EJECUTAR_ACCION, _aceptacion_proceso_comercial),
    EntradaAccion('PATCH', re.compile(r'^/procesos-comerciales/(?P<id>\d+)/fecha-estimada-cierre$'), EventoAuditoria.ACTUALIZAR, _fecha_estimada_cierre),
    EntradaAccion('PATCH', re.compile(r'^/procesos-comerciales/(?P<id>\d+)/probabilidad-cierre-ejecutivo$'), EventoAuditoria.ACTUALIZAR, _probabilidad_cierre),
    EntradaAccion('POST', re.compile(r'^/procesos-comerciales/(?P<id>\d+)/solicitudes-cotizacion$'), EventoAuditoria.CREAR, _solicitar_cotizacion),
    EntradaAccion('POST', re.compile(r'^/procesos-comerciales/(?P<id>\d+)/solicitudes-cotizacion/recotizacion$'), EventoAuditoria.CREAR, _solicitar_recotizacion),
    EntradaAccion('POST', re.compile(r'^/procesos-comerciales/(?P<id>\d+)/polizas$'), EventoAuditoria.CREAR, _registrar_poliza_en_oportunidad),
    # Pólizas y cuotas
    EntradaAccion('POST', re.compile(r'^/polizas/(?P<numero>[^/]+)/registrar-renovacion-cotizada$'), EventoAuditoria.EJECUTAR_ACCION, _registrar_renovacion_cotizada),
    EntradaAccion('POST', re.compile(r'^/polizas/(?P<numero>[^/]+)/plan-pago$'), EventoAuditoria.CREAR, _crear_plan_pago),
    EntradaAccion('POST', re.compile(r'^/polizas/(?P<numero>[^/]+)/cancelar$'), EventoAuditoria.EJECUTAR_ACCION, _cancelar_poliza),
    EntradaAccion('POST', re.compile(r'^/polizas/(?P<numero>[^/]+)/reactivar$'), EventoAuditoria.EJECUTAR_ACCION, _reactivar_poliza),
    EntradaAccion('PUT', re.compile(r'^/polizas/(?P<numero>[^/]+)$'), EventoAuditoria.ACTUALIZAR, _actualizar_poliza),
    EntradaAccion('POST', re.compile(r'^/cuota/(?P<id>\d+)/pagar$'), EventoAuditoria.EJECUTAR_ACCION, _pagar_cuota),
    # Solicitudes de cotización y estudios
    EntradaAccion('POST', re.compile(r'^/solicitudes-cotizacion/(?P<id>\d+)/cotizaciones$'), EventoAuditoria.CREAR, _registrar_cotizacion),
    EntradaAccion('POST', re.compile(r'^/solicitudes-cotizacion/(?P<id>\d+)/estudios-comerciales$'), EventoAuditoria.CREAR, _subir_estudio_comercial),
    EntradaAccion('POST', re.compile(r'^/estudio-comercial/?$'), EventoAuditoria.CREAR, _generar_estudio_comercial),
    # Gestión comercial
    EntradaAccion('POST', re.compile(r'^/gestiones-comerciales/?$'), EventoAuditoria.CREAR, _registrar_gestion_comercial),
    # Usuarios
    EntradaAccion('POST', re.compile(r'^/usuarios/?$'), EventoAuditoria.CREAR, _registrar_usuario),
    EntradaAccion('PUT', re.compile(r'^/usuarios/(?P<rut>[^/]+)$'), EventoAuditoria.ACTUALIZAR, _actualizar_usuario),
    EntradaAccion('DELETE', re.compile(r'^/usuarios/(?P<rut>[^/]+)$'), EventoAuditoria.ELIMINAR, _eliminar_usuario),
    # Administradores
    EntradaAccion('POST', re.compile(r'^/administradores/?$'), EventoAuditoria.CREAR, _registrar_administrador),
    EntradaAccion('PUT', re.compile(r'^/administradores/(?P<id>\d+)$'), EventoAuditoria.ACTUALIZAR, _actualizar_administrador),
    # Compañías de seguros
    EntradaAccion('POST', re.compile(r'^/companies-seguros/?$'), EventoAuditoria.CREAR, _crear_company),
    EntradaAccion('PUT', re.compile(r'^/companies-seguros/(?P<id>\d+)$'), EventoAuditoria.ACTUALIZAR, _actualizar_company),
    EntradaAccion('PUT', re.compile(r'^/companies-seguros/(?P<id>\d+)/factores-cuotas$'), EventoAuditoria.EJECUTAR_ACCION, _actualizar_factores_cuotas),
    EntradaAccion('DELETE', re.compile(r'^/companies-seguros/(?P<id>\d+)$'), EventoAuditoria.ELIMINAR, _eliminar_company),
    # Productos
    EntradaAccion('POST', re.compile(r'^/productos/?$'), EventoAuditoria.CREAR, _crear_producto),
    EntradaAccion('PUT', re.compile(r'^/productos/(?P<id>\d+)$'), EventoAuditoria.ACTUALIZAR, _actualizar_producto),
    EntradaAccion('DELETE', re.compile(r'^/productos/(?P<id>\d+)$'), EventoAuditoria.ELIMINAR, _eliminar_producto),
    # Recordatorios
    EntradaAccion('POST', re.compile(r'^/recordatorios/?$'), EventoAuditoria.CREAR, _registrar_recordatorio),
    EntradaAccion('PATCH', re.compile(r'^/recordatorios/(?P<id>\d+)$'), EventoAuditoria.ACTUALIZAR, _actualizar_recordatorio),
    EntradaAccion('PATCH', re.compile(r'^/recordatorios/(?P<id>\d+)/completar$'), EventoAuditoria.EJECUTAR_ACCION, _completar_recordatorio),
    EntradaAccion('DELETE', re.compile(r'^/recordatorios/(?P<id>\d+)$'), EventoAuditoria.ELIMINAR, _eliminar_recordatorio),
    # Notificaciones
    EntradaAccion('PATCH', re.compile(r'^/notificaciones/(?P<id>\d+)/leer$'), EventoAuditoria.EJECUTAR_ACCION, _marcar_notificacion_leida),
    EntradaAccion('POST', re.compile(r'^/notificaciones/leer-todas$'), EventoAuditoria.EJECUTAR_ACCION, _marcar_todas_notificaciones_leidas),
    # Configuración de condominio
    EntradaAccion('PUT', re.compile(r'^/configuracion-condominio/valor-uf-region$'), EventoAuditoria.ACTUALIZAR, _guardar_valor_uf_region),
    EntradaAccion('DELETE', re.compile(r'^/configuracion-condominio/valor-uf-region/(?P<id>\d+)$'), EventoAuditoria.ELIMINAR, _eliminar_valor_uf_region),
    EntradaAccion('PUT', re.compile(r'^/configuracion-condominio/parametros-depreciacion$'), EventoAuditoria.ACTUALIZAR, _guardar_parametros_depreciacion),
    # Comunicados de gerencia
    EntradaAccion('POST', re.compile(r'^/comunicados-gerencia/?$'), EventoAuditoria.CREAR, _publicar_comunicado),
]
