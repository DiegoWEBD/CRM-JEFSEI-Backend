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

# Notificaciones de cambio de asignación.
TIPO_ASIGNACION = 'ASIGNACION_EJECUTIVO'
TIPO_DESASIGNACION = 'DESASIGNACION_EJECUTIVO'

# Roles con asignación por proceso (dueños de alertas por estado).
ROL_EJECUTIVO_COMERCIAL = 'EJECUTIVO_COMERCIAL'
ROL_EJECUTIVO_EVALUACION_PROYECTOS = 'EJECUTIVO_EVALUACION_PROYECTOS'

# Rol destinatario de las alertas de renovación cuando el cliente no
# tiene ejecutivo ni asistente de renovación asignados.
ROL_EJECUTIVO_RENOVACION = 'EJECUTIVO_RENOVACION'
