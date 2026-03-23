from model.entity_set_link import EntitySetLinkDef
from .entity_set_link_validator import validate_entity_set_link_schema
from .errors import ParseError

def parse_entity_set_link(data: dict) -> EntitySetLinkDef:
    """
    解析 entity_set_link。
    """
    validate_entity_set_link_schema(data)

    try:
        metadata = data["metadata"]
        spec = data["spec"]
        
        domain = metadata["domain"]
        name = metadata["name"]
        full_name = name if "." in name else f"{domain}.{name}"

        src = spec["src"]
        dest = spec["dest"]

        return EntitySetLinkDef(
            domain=domain,
            name=name,
            full_name=full_name,
            src_kind=src["kind"],
            src_domain=src["domain"],
            src_name=src["name"],
            entity_link_type=spec["entity_link_type"],
            dest_kind=dest["kind"],
            dest_domain=dest["domain"],
            dest_name=dest["name"]
        )
    except Exception as e:
        raise ParseError(f"解析 EntitySetLinkDef 失败: {str(e)}")
