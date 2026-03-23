from .common_validator import validate_common_metadata
from .errors import SchemaValidationError

def validate_entity_set_link_schema(data: dict) -> None:
    """
    校验 entity_set_link 的 Schema。
    """
    # 通用校验已包含 kind, metadata.domain, metadata.name, spec 的存在性校验
    _, spec = validate_common_metadata(data, "entity_set_link")

    # 校验 src
    src = spec.get("src")
    if not isinstance(src, dict):
        raise SchemaValidationError("spec.src 必须为 dict")
    if src.get("kind") != "entity_set":
        raise SchemaValidationError("spec.src.kind 必须为 entity_set")
    if not src.get("domain"):
        raise SchemaValidationError("spec.src.domain 必填")
    if not src.get("name"):
        raise SchemaValidationError("spec.src.name 必填")

    # 校验 link_type
    if not spec.get("entity_link_type"):
        raise SchemaValidationError("spec.entity_link_type 必填")

    # 校验 dest
    dest = spec.get("dest")
    if not isinstance(dest, dict):
        raise SchemaValidationError("spec.dest 必须为 dict")
    if dest.get("kind") != "entity_set":
        raise SchemaValidationError("spec.dest.kind 必须为 entity_set")
    if not dest.get("domain"):
        raise SchemaValidationError("spec.dest.domain 必填")
    if not dest.get("name"):
        raise SchemaValidationError("spec.dest.name 必填")
    
    # 其他字段（如 filter_by_entity, priority 等）当前阶段作为可选，不进行强制校验
