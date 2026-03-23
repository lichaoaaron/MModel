from dataclasses import dataclass

@dataclass
class EntitySetLinkDef:
    domain: str
    name: str
    full_name: str
    src_kind: str
    src_domain: str
    src_name: str
    entity_link_type: str
    dest_kind: str
    dest_domain: str
    dest_name: str
