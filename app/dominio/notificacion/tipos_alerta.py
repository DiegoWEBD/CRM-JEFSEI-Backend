# Tipos de alerta basadas en la fecha estimada de cierre de un proceso
# comercial. Se marcan leídas al cerrar el proceso, al (re)establecer su
# fecha de cierre y al cambiar el ejecutivo comercial asignado.
TIPOS_ALERTA_FECHA = ('CIERRE_ESTIMADO_PROXIMO', 'FECHA_CIERRE_VENCIDA')

# Alertas de permanencia en estado (SLA).
TIPOS_ALERTA_SLA = ('SLA_POR_VENCER', 'SLA_VENCIDO')

# Alertas de renovación de pólizas (basadas en el fin de vigencia).
# Se marcan leídas al cambiar el fin de vigencia de la póliza y al
# iniciar el proceso comercial de renovación de la misma.
TIPOS_ALERTA_RENOVACION = (
    'RENOVACION_COTIZACION_PENDIENTE',
    'RENOVACION_GESTION_PENDIENTE',
    'RENOVACION_POLIZA_VENCIDA',
)

# Escalonamiento de alertas: cuando una alerta de la clave aplica para la
# entidad, las de nivel inferior listadas dejan de ser relevantes y se
# marcan leídas en la misma corrida del scheduler (p. ej. al vencer la
# fecha de cierre, el aviso de "cierre próximo" ya no aplica).  Las alertas
# SLA no escalan por tipo: sus recordatorios por tramo (70/100/130/...)
# escalan vía ServicioAlertasProceso.marcar_leidas_sla_anteriores.
ALERTAS_RESUELTAS_POR: dict[str, tuple[str, ...]] = {
    'RENOVACION_GESTION_PENDIENTE': ('RENOVACION_COTIZACION_PENDIENTE',),
    'RENOVACION_POLIZA_VENCIDA': (
        'RENOVACION_COTIZACION_PENDIENTE',
        'RENOVACION_GESTION_PENDIENTE',
    ),
    'FECHA_CIERRE_VENCIDA': ('CIERRE_ESTIMADO_PROXIMO',),
}


def tipos_resueltos_por(codigos_aplicables) -> tuple[str, ...]:
    """Tipos de alerta a marcar leídas al aplicar los tipos dados.

    Unión sin duplicados y en orden estable de los escalones inferiores de
    cada tipo aplicable."""
    resueltos: set[str] = set()

    for codigo in codigos_aplicables:
        resueltos.update(ALERTAS_RESUELTAS_POR.get(codigo, ()))

    return tuple(sorted(resueltos))

# Notificaciones de cambio de asignación.
TIPO_ASIGNACION = 'ASIGNACION_EJECUTIVO'
TIPO_DESASIGNACION = 'DESASIGNACION_EJECUTIVO'

# Roles con asignación por proceso (dueños de alertas por estado).
ROL_EJECUTIVO_COMERCIAL = 'EJECUTIVO_COMERCIAL'
ROL_EJECUTIVO_EVALUACION_PROYECTOS = 'EJECUTIVO_EVALUACION_PROYECTOS'

# Roles de renovacion con asignacion por cliente (duenos de las
# alertas de las oportunidades de renovacion).
ROL_EJECUTIVO_RENOVACION = 'EJECUTIVO_RENOVACION'
ROL_ASISTENTE_RENOVACION = 'ASISTENTE_RENOVACION'
