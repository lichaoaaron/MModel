from .errors import SchemaValidationError

ALLOWED_SYSTEM_TIME_FIELDS = {"__time__"}

def validate_entity_set_schema(data: dict) -> None:
    """
    校验 entity_set 的 Schema 完整性和合法性。
    
    Args:
        data: 加载后的 YAML 数据字典
        
    Raises:
        SchemaValidationError: 校验不通过时抛出
    """
    # 1. 基础结构校验
    if data.get("kind") != "entity_set":
        raise SchemaValidationError("kind 必须为 entity_set")
    
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        raise SchemaValidationError("metadata 必须存在且为 dict")
    
    # 2. metadata 校验
    if not metadata.get("domain"):
        raise SchemaValidationError("metadata.domain 必填")
    if not metadata.get("name"):
        raise SchemaValidationError("metadata.name 必填")
        
    display_name = metadata.get("display_name")
    if not isinstance(display_name, dict):
        raise SchemaValidationError("metadata.display_name 必须存在且为 dict")
    if not display_name.get("zh_cn"):
        raise SchemaValidationError("metadata.display_name.zh_cn 必填")
        
    # 3. spec 基础结构校验
    spec = data.get("spec")
    if not isinstance(spec, dict):
        raise SchemaValidationError("spec 必须存在且为 dict")
        
    # time_field 和 id_generator 不再强制必填
    time_field = spec.get("time_field")
        
    # 4. fields 校验
    fields = spec.get("fields")
    if not isinstance(fields, list) or not fields:
        raise SchemaValidationError("spec.fields 必须为非空 list")
        
    allowed_types = {"string", "int", "long", "json", "json_object", "integer", "boolean", "time"}
    field_names = set()
    
    for i, field_item in enumerate(fields):
        if not isinstance(field_item, dict):
            raise SchemaValidationError(f"spec.fields[{i}] 必须为 dict")
        
        name = field_item.get("name")
        if not name:
            raise SchemaValidationError(f"spec.fields[{i}].name 必填")
        
        f_type = field_item.get("type")
        if not f_type:
            raise SchemaValidationError(f"spec.fields[{i}].type 必填")
        if f_type not in allowed_types:
            raise SchemaValidationError(f"spec.fields[{i}].type '{f_type}' 不在允许范围内 {allowed_types}")
            
        field_names.add(name)

    # 5. 逻辑关联校验
    # 只有当 time_field 存在时才进行校验
    if time_field:
        if time_field not in field_names and time_field not in ALLOWED_SYSTEM_TIME_FIELDS:
            raise SchemaValidationError(f"spec.time_field '{time_field}' 必须存在于 spec.fields 中，或属于允许的系统时间字段 {ALLOWED_SYSTEM_TIME_FIELDS}")
        
    primary_key_fields = spec.get("primary_key_fields")
    if not isinstance(primary_key_fields, list) or not primary_key_fields:
        raise SchemaValidationError("spec.primary_key_fields 必须为非空 list")
        
    for pk in primary_key_fields:
        if pk not in field_names:
            raise SchemaValidationError(f"spec.primary_key_fields 中字段不存在: {pk}")
