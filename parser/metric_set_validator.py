from .errors import SchemaValidationError
from .common_validator import validate_common_metadata

def validate_metric_set_schema(data: dict) -> tuple[dict, dict]:
    """
    校验 metric_set 的 Schema 规则
    """
    # 1. 基础结构校验
    metadata, spec = validate_common_metadata(data, "metric_set")

    # 2. metadata.display_name.zh_cn 必填
    if not metadata.get("display_name", {}).get("zh_cn"):
        raise SchemaValidationError("metadata.display_name.zh_cn 必填")

    # 3. spec.query_type 校验
    query_type = spec.get("query_type")
    # 扩充允许值：新增 prom, spl
    allowed_query_types = {"prometheus", "cms", "prom", "spl", "sql"}
    if query_type and query_type not in allowed_query_types:
        raise SchemaValidationError(f"spec.query_type '{query_type}' 不在允许范围内 {allowed_query_types}")

    # 4. spec.metrics 校验
    metrics = spec.get("metrics")
    if not isinstance(metrics, list) or len(metrics) == 0:
        raise SchemaValidationError("spec.metrics 必须为非空数组")

    for i, m in enumerate(metrics):
        if not m.get("name"):
            raise SchemaValidationError(f"spec.metrics[{i}].name 必填")
        
        # display_name 改为可选
        
        agg = m.get("aggregator")
        # aggregator 允许为空字符串
        if agg and agg != "":
            allowed_aggregators = {"avg", "sum", "max", "min", "count", "p50", "p90", "p95", "p99"}
            if agg not in allowed_aggregators:
                raise SchemaValidationError(f"spec.metrics[{i}].aggregator '{agg}' 不在允许范围内 {allowed_aggregators}")
            
        m_type = m.get("type")
        # type 支持 histogram, None, "None", ""
        if m_type not in [None, "None", ""]:
            allowed_metric_types = {"gauge", "counter", "histogram", "summary"}
            if m_type not in allowed_metric_types:
                raise SchemaValidationError(f"spec.metrics[{i}].type '{m_type}' 不在允许范围内 {allowed_metric_types}")
        
        # unit 改为可选，不再抛出异常

    # 5. spec.labels.keys 校验
    labels = spec.get("labels", {})
    label_keys = labels.get("keys")
    if not isinstance(label_keys, list):
        raise SchemaValidationError("spec.labels.keys 必填且必须为数组")

    allowed_label_types = {"string", "int", "integer", "long", "boolean"}
    for i, lk in enumerate(label_keys):
        if not lk.get("name"):
            raise SchemaValidationError(f"spec.labels.keys[{i}].name 必填")
        lk_type = lk.get("type")
        if lk_type not in allowed_label_types:
            raise SchemaValidationError(f"spec.labels.keys[{i}].type '{lk_type}' 不在允许范围内 {allowed_label_types}")

    return metadata, spec
