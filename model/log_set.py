from dataclasses import dataclass, field
from .entity_set import FieldDef

@dataclass
class LogSetDef:
    domain: str
    name: str
    full_name: str
    time_field: str
    fields: list[FieldDef] = field(default_factory=list)
