from model.log_set import LogSetDef
from model.entity_set import FieldDef
from .log_set_validator import validate_log_set_schema
from .errors import ParseError

def parse_log_set(data: dict) -> LogSetDef:
    """
    解析 log_set。
    """
    validate_log_set_schema(data)

    try:
        metadata = data["metadata"]
        spec = data["spec"]
        
        domain = metadata["domain"]
        name = metadata["name"]
        full_name = name if "." in name else f"{domain}.{name}"

        # 类型归一化
        type_mapping = {
            "integer": "int",
            "long": "int",
            "json_object": "json",
            "object": "json",      # 归一化为 json
            "number": "number",    # 归一化为 number
            "float": "number",     # 归一化为 number
            "double": "number",    # 归一化为 number
            "boolean": "bool",
            "time": "time",
            "string": "string",
            "int": "int",
            "json": "json"
        }

        fields = []
        for f in spec["fields"]:
            raw_type = str(f.get("type", ""))
            normalized_type = type_mapping.get(raw_type, raw_type)
            fields.append(FieldDef(name=str(f.get("name", "")), type=normalized_type))

        return LogSetDef(
            domain=domain,
            name=name,
            full_name=full_name,
            time_field=spec["time_field"],
            fields=fields
        )
    except Exception as e:
        raise ParseError(f"解析 LogSetDef 失败: {str(e)}")
