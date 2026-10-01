from dataclasses import dataclass, field


@dataclass
class EntidadAuditada:
    etiqueta: str
    nombre: str | None = None
    identificador: str | int | None = None
    propietario: 'EntidadAuditada | None' = None
    entrecomillado: bool = False


@dataclass
class FragmentoFrase:
    preposicion: str = ''
    entidad: EntidadAuditada | None = None
    texto: str | None = None


@dataclass
class AccionDescrita:
    evento: str
    verbo: str
    fragmentos: list[FragmentoFrase] = field(default_factory=list)
    sufijo: str | None = None
