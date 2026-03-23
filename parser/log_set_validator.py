from .errors import SchemaValidationError
from .common_validator import validate_common_metadata

def validate_log_set_schema(data: dict) -> tuple[dict, dict]:
    """
    校验 log_set 的 Schema 规则
    返回 (metadata, spec) 元组。
    """
    # 1. 基础结构校验 (kind, metadata, spec)
    metadata, spec = validate_common_metadata(data, "log_set")

    # 1. 校验 metadata.display_name.zh_cn (针对 log_set 是必填)
    display_name = metadata.get("display_name")
    if not isinstance(display_name, dict) or not display_name.get("zh_cn"):
        raise SchemaValidationError("metadata.display_name.zh_cn 必填")

    # 2. 校验 spec.time_field
    time_field = spec.get("time_field")
    if not time_field:
        raise SchemaValidationError("spec.time_field 必填")

    # 3. 校验 spec.fields
    fields = spec.get("fields")
    if not isinstance(fields, list) or not fields:
        raise SchemaValidationError("spec.fields 必须为非空 list")

    field_names = []
    # 扩充允许的类型，包含真实样本中的 object, number, float, double
    allowed_types = {
        "string", "int", "integer", "long", "json", "json_object", 
        "boolean", "time", "object", "number", "float", "double"
    }

    for i, f in enumerate(fields):
        name = f.get("name")
        f_type = f.get("type")
        
        if not name:
            raise SchemaValidationError(f"spec.fields[{i}].name 必填")
        if not f_type:
            raise SchemaValidationError(f"spec.fields[{i}].type 必填 (字段: {name})")
        
        if f_type not in allowed_types:
            raise SchemaValidationError(f"spec.fields[{i}].type '{f_type}' 不在允许范围内 {allowed_types}")
        
        field_names.append(name)

    # 5. time_field 校验逻辑：如果是系统保留字段 "__time__"，允许不在 fields 中定义
    if time_field != "__time__" and time_field not in field_names:
        raise SchemaValidationError(f"spec.time_field '{time_field}' 必须存在于 spec.fields 中")

    return metadata, spec
