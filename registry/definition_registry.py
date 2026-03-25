from typing import Dict, List, Any, Optional
from parser.errors import DuplicateDefinitionError

class DefinitionRegistry:
    """定义注册中心，用于存储和检索所有解析后的定义对象"""
    
    def __init__(self):
        # 按照 kind 分类存储: full_name -> definition_obj
        self._entity_sets: Dict[str, Any] = {}
        self._entity_set_links: Dict[str, Any] = {}
        self._metric_sets: Dict[str, Any] = {}
        self._log_sets: Dict[str, Any] = {}
        self._trace_sets: Dict[str, Any] = {}
        
        # 映射 full_name -> source_file
        self._source_files: Dict[str, str] = {}
        
        # 映射 kind -> 对应的存储字典
        self._store_map = {
            "entity_set": self._entity_sets,
            "entity_set_link": self._entity_set_links,
            "metric_set": self._metric_sets,
            "log_set": self._log_sets,
            "trace_set": self._trace_sets,
        }

    def _get_full_name(self, obj: Any) -> str:
        if hasattr(obj, "full_name") and obj.full_name:
            return obj.full_name
        if hasattr(obj, "domain") and hasattr(obj, "name"):
            return f"{obj.domain}.{obj.name}"
        raise ValueError(f"无法获取对象的 full_name: {obj}")

    def register(self, definition_obj: Any, source_file: Optional[str] = None) -> None:
        kind = getattr(definition_obj, "kind", None)
        if not kind or kind not in self._store_map:
            raise ValueError(f"不支持的定义类型或缺少 kind 属性: {kind}")
            
        full_name = self._get_full_name(definition_obj)
        store = self._store_map[kind]
        
        if full_name in store:
            existing_file = self._source_files.get(full_name, "unknown")
            new_file = source_file or "unknown"
            raise DuplicateDefinitionError(
                f"发现重复的定义 '{full_name}' (类型: {kind})。\n"
                f"已存在于: {existing_file}\n"
                f"冲突文件: {new_file}"
            )
            
        store[full_name] = definition_obj
        if source_file:
            self._source_files[full_name] = source_file

    def get_source_file(self, full_name: str) -> Optional[str]:
        return self._source_files.get(full_name)

    # --- Fetch Methods ---
    def get_entity_set(self, full_name: str) -> Optional[Any]:
        return self._entity_sets.get(full_name)

    def get_entity_set_link(self, full_name: str) -> Optional[Any]:
        return self._entity_set_links.get(full_name)

    def get_metric_set(self, full_name: str) -> Optional[Any]:
        return self._metric_sets.get(full_name)

    def get_log_set(self, full_name: str) -> Optional[Any]:
        return self._log_sets.get(full_name)

    def get_trace_set(self, full_name: str) -> Optional[Any]:
        return self._trace_sets.get(full_name)

    # --- Has Methods ---
    def has_entity_set(self, full_name: str) -> bool:
        return full_name in self._entity_sets

    # --- List Methods ---
    def list_entity_sets(self) -> List[Any]:
        return list(self._entity_sets.values())

    def list_entity_set_links(self) -> List[Any]:
        return list(self._entity_set_links.values())

    def list_metric_sets(self) -> List[Any]:
        return list(self._metric_sets.values())

    def list_log_sets(self) -> List[Any]:
        return list(self._log_sets.values())

    def list_trace_sets(self) -> List[Any]:
        return list(self._trace_sets.values())

    def list_all(self) -> List[Any]:
        all_defs = []
        for store in self._store_map.values():
            all_defs.extend(store.values())
        return all_defs
