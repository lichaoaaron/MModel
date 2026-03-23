from .metric_set_validator import validate_metric_set_schema
from model.metric_set import MetricSetDef

def parse_metric_set(data: dict) -> MetricSetDef:
    # 只需要保留校验和 from_dict 调用即可，不需要在 parser 复写一遍解析逻辑
    metadata, spec = validate_metric_set_schema(data)

    # 1. 转换数据
    # 这里直接复用 MetricSetDef.from_dict 逻辑以保持一致性
    # 先把 metadata 和 spec 给 data
    data["metadata"] = metadata
    data["spec"] = spec
    
    return MetricSetDef.from_dict(data)
