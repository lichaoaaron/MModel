from .entity_set_parser import parse_entity_set
from .entity_set_link_parser import parse_entity_set_link
from .log_set_parser import parse_log_set
from .errors import ParseError

def parse_definition(data: dict):
    """
    统一分发入口：根据 kind 自动调用对应 parser。
    """
    kind = data.get("kind")
    if not kind:
        raise ParseError("YAML 缺失 kind 字段")

    if kind == "entity_set":
        return parse_entity_set(data)
    elif kind == "entity_set_link":
        return parse_entity_set_link(data)
    elif kind == "log_set":
        return parse_log_set(data)
    elif kind in ["metric_set", "trace_set", "event_set"]:
        # 预留占位符，后续实现
        raise ParseError(f"当前暂不支持解析 kind: {kind}，正在开发中")
    else:
        raise ParseError(f"未知的 kind 类型: {kind}")
