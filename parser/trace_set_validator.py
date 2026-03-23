from .errors import SchemaValidationError
from .common_validator import validate_common_metadata

def validate_trace_set_schema(data: dict) -> tuple[dict, dict]:
    """
    校验 trace_set 的 Schema 规则
    """
    # 1. 基础结构校验
    metadata, spec = validate_common_metadata(data, "trace_set")

    # 2. metadata 校验
    display_name = metadata.get("display_name", {})
    if not isinstance(display_name, dict) or not display_name.get("zh_cn"):
        raise SchemaValidationError("metadata.display_name.zh_cn 必填")

    # 3. spec 必填字段校验
    required_spec_fields = [
        "protocol", "time_field", "trace_id_field", "span_id_field", "parent_span_id_field"
    ]
    for field_name in required_spec_fields:
        if not spec.get(field_name):
            raise SchemaValidationError(f"spec.{field_name} 必填")

    # 4. 协议校验
    allowed_protocols = {"otel", "skywalking"}
    if spec["protocol"] not in allowed_protocols:
        raise SchemaValidationError(f"spec.protocol '{spec['protocol']}' 不在允许范围内 {allowed_protocols}")

    # 5. fields 校验
    fields = spec.get("fields")
    if not isinstance(fields, list) or len(fields) == 0:
        raise SchemaValidationError("spec.fields 必填且不能为空数组")

    field_names = []
    allowed_types = {"string", "int", "integer", "long", "json", "json_object", "boolean", "time"}

    for i, f in enumerate(fields):
        name = f.get("name")
        f_type = f.get("type")
        if not name:
            raise SchemaValidationError(f"spec.fields[{i}].name 必填")
        if f_type not in allowed_types:
            raise SchemaValidationError(f"spec.fields[{i}].type '{f_type}' 不在允许范围内 (字段: {name})")
        field_names.append(name)

    # 6. 关联性校验
    for f_ref in ["time_field", "trace_id_field", "span_id_field", "parent_span_id_field"]:
        val = spec[f_ref]
        # 如果是系统保留字段 "__time__"，允许不在 fields 中定义
        if f_ref == "time_field" and val == "__time__":
            continue
        if val not in field_names:
            raise SchemaValidationError(f"spec.{f_ref} '{val}' 必须存在于 spec.fields 中")

    return metadata, spec
