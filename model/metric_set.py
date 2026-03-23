from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class MetricDef:
    name: str
    display_name: str = ""
    description: str = ""
    aggregator: Optional[str] = None
    type: Optional[str] = None
    unit: Optional[str] = None  # 新增 unit 字段到 dataclass

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetricDef':
        # 归一化 aggregator: "" -> None, type: ""/None/"None" -> None
        agg = data.get("aggregator")
        if not agg:
            agg = None
            
        m_type = data.get("type")
        if not m_type or m_type in ["None", ""]:
            m_type = None

        return cls(
            name=data["name"],
            display_name=data.get("display_name", {}).get("zh_cn", "") if isinstance(data.get("display_name"), dict) else data.get("display_name", ""),
            description=data.get("description", ""),
            aggregator=agg,
            type=m_type,
            unit=data.get("unit")
        )

@dataclass
class LabelKeyDef:
    name: str
    type: str
    display_name_zh: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LabelKeyDef':
        return cls(
            name=data["name"],
            type=data.get("type", "string"),
            display_name_zh=data.get("display_name_zh")
        )

@dataclass
class MetricSetDef:
    # 基础元数据
    name: str
    kind: str = "metric_set"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 核心字段 (通常在 spec 中，但展开为顶层属性便于访问)
    domain: str = ""
    full_name: str = ""
    query_type: Optional[str] = None
    description: Optional[str] = None
    
    metrics: List[MetricDef] = field(default_factory=list)
    label_keys: List[LabelKeyDef] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetricSetDef':
        spec = data.get("spec", {})
        metadata = data.get("metadata", {})
        
        metrics = [MetricDef.from_dict(m) for m in spec.get("metrics", [])]
        
        # 兼容旧版的 labels.keys 取值
        labels = spec.get("labels", {})
        keys = labels.get("keys", [])
        label_keys = [LabelKeyDef.from_dict(lk) for lk in keys]
        
        # query_type 归一化逻辑 (prom -> prometheus)
        raw_query_type = spec.get("query_type")
        normalized_query_type = "prometheus" if raw_query_type == "prom" else raw_query_type

        return cls(
            name=data.get("name") or metadata.get("name", ""),
            kind=data.get("kind", "metric_set"),
            metadata=metadata,
            domain=metadata.get("domain", ""),
            full_name=metadata.get("name", ""),
            query_type=normalized_query_type,
            description=metadata.get("description"),
            metrics=metrics,
            label_keys=label_keys
        )
