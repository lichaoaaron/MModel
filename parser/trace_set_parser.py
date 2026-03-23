from .trace_set_validator import validate_trace_set_schema
from model.trace_set import TraceSetDef
from model.entity_set import FieldDef

def parse_trace_set(data: dict) -> TraceSetDef:
    metadata, spec = validate_trace_set_schema(data)

    # 类型归一化
    type_map = {
        "integer": "int",
        "long": "int",
        "json_object": "json",
        "boolean": "bool",
        "time": "time"
    }

    parsed_fields = []
    for f in spec.get("fields", []):
        raw_type = f.get("type", "string")
        field_obj = FieldDef(
            name=f["name"],
            type=type_map.get(raw_type, raw_type),
            display_name=f.get("display_name", {}).get("zh_cn", f["name"]),
            description=f.get("description")
        )
        parsed_fields.append(field_obj)

    domain = metadata["domain"]
    name = metadata["name"]

    return TraceSetDef(
        domain=domain,
        name=name,
        full_name=f"{domain}.{name}",
        display_name=metadata["display_name"]["zh_cn"],
        protocol=spec["protocol"],
        time_field=spec["time_field"],
        trace_id_field=spec["trace_id_field"],
        span_id_field=spec["span_id_field"],
        parent_span_id_field=spec["parent_span_id_field"],
        fields=parsed_fields,
        description=metadata.get("description")
    )
