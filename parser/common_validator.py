from .errors import SchemaValidationError

def validate_common_metadata(data: dict, expected_kind: str) -> tuple[dict, dict]:
    """
    校验通用的 kind, metadata 和 spec 结构。
    返回 (metadata, spec) 元组。
    """
    if not isinstance(data, dict):
        raise SchemaValidationError("YAML 顶层格式错误，应为 dict")

    if data.get("kind") != expected_kind:
        raise SchemaValidationError(f"kind 必须为 {expected_kind}")

    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        raise SchemaValidationError("metadata 必须存在且为 dict")

    spec = data.get("spec")
    if not isinstance(spec, dict):
        raise SchemaValidationError("spec 必须存在且为 dict")

    if not metadata.get("domain"):
        raise SchemaValidationError("metadata.domain 必填")
    if not metadata.get("name"):
        raise SchemaValidationError("metadata.name 必填")

    return metadata, spec
