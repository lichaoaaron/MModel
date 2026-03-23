from dataclasses import dataclass, field
from typing import Optional

@dataclass
class FieldDef:
    name: str
    type: str
    display_name: Optional[str] = None
    description: Optional[str] = None

@dataclass
class EntitySetDef:
    domain: str
    name: str
    full_name: str
    id_generator: Optional[str] = None
    time_field: Optional[str] = None
    primary_key_fields: list[str] = field(default_factory=list)
    name_fields: list[str] = field(default_factory=list)
    keep_alive_seconds: Optional[int] = None
    dynamic: bool = False
    fields: list[FieldDef] = field(default_factory=list)
