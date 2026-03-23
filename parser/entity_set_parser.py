from model.entity_set import EntitySetDef, FieldDef
from .entity_set_validator import validate_entity_set_schema
from .errors import ParseError

def parse_entity_set(data: dict) -> EntitySetDef:
    """
    将字典数据解析为 EntitySetDef 对象。
    
    Args:
        data: YAML 内容字典
        
    Returns:
        EntitySetDef: 解析后的对象
        
    Raises:
        SchemaValidationError: 校验失败时抛出
        ParseError: 解析逻辑错误时抛出
    """
    # 1. 先进行 Schema 校验
    validate_entity_set_schema(data)
    
    try:
        metadata = data["metadata"]
        spec = data["spec"]
        
        domain = metadata["domain"]
        name = metadata["name"]
        
        # 字段类型归一化映射
        type_mapping: dict[str, str] = {
            "json_object": "json",
            "integer": "int",
            "boolean": "bool",
            "time": "time"
        }
        
        # full_name 规则处理
        if "." in name:
            full_name = name
        else:
            full_name = f"{domain}.{name}"
            
        # 处理 id_generator 和 time_field
        pk_fields = spec.get("primary_key_fields", [])
        id_generator = spec.get("id_generator")
        if not id_generator:
            pk_str = ",".join(pk_fields)
            id_generator = f"auto_by_pk({pk_str})"
            
        time_field = spec.get("time_field")

        # 转换 fields
        fields = []
        for f in spec["fields"]:
            # 类型校验已在 validator 中完成，此处做归一化并确保为 str
            raw_type = str(f.get("type", ""))
            normalized_type = type_mapping.get(raw_type, raw_type)
            fields.append(FieldDef(name=str(f.get("name", "")), type=normalized_type))
        
        # 构造对象
        return EntitySetDef(
            domain=domain,
            name=name,
            full_name=full_name,
            id_generator=id_generator,
            time_field=time_field,
            primary_key_fields=pk_fields,
            name_fields=spec.get("name_fields", []),
            keep_alive_seconds=spec.get("keep_alive_seconds"),
            dynamic=spec.get("dynamic", False),
            fields=fields
        )
    except Exception as e:
        raise ParseError(f"解析 EntitySetDef 失败: {str(e)}")
