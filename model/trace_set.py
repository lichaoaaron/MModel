from dataclasses import dataclass, field
from typing import List, Optional
from .entity_set import FieldDef

@dataclass
class TraceSetDef:
    domain: str
    name: str
    full_name: str  # {domain}.{name}
    display_name: str
    protocol: str
    time_field: str
    trace_id_field: str
    span_id_field: str
    parent_span_id_field: str
    fields: List[FieldDef] = field(default_factory=list)
    description: Optional[str] = None
