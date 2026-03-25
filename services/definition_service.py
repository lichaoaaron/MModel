from typing import Any, List, Dict, Optional, Union
from pathlib import Path
from registry.definition_registry import DefinitionRegistry
from registry.definition_loader import DefinitionLoader
from parser.errors import ServiceNotLoadedError, DefinitionNotFoundError, DefinitionLoadError

class DefinitionService:
    """提供统一、稳定、面向业务调用的服务类"""

    def __init__(self):
        self._registry: Optional[DefinitionRegistry] = None
        self._base_dir: Optional[Path] = None
        self._validate_dependencies: bool = True

    def load_from_dir(self, base_dir: Union[str, Path], validate_dependencies: bool = True, debug: bool = False) -> None:
        """从指定目录加载所有定义"""
        dir_path = Path(base_dir)
        if not dir_path.exists() or not dir_path.is_dir():
            raise DefinitionLoadError(f"指定的目录不存在: {dir_path.absolute()}")
            
        self._base_dir = dir_path
        self._validate_dependencies = validate_dependencies
        self._reload_internal(debug=debug)

    def reload(self, debug: bool = False) -> None:
        """重新加载当前目录的定义"""
        if not self._base_dir:
            raise ServiceNotLoadedError("尚未指定基础目录，无法 reload。请先调用 load_from_dir")
        self._reload_internal(debug=debug)

    def _reload_internal(self, debug: bool = False) -> None:
        """内部重载逻辑"""
        if self._base_dir is None:
            return
            
        self._registry = DefinitionLoader.load_from_directory(
            self._base_dir, 
            validate_dependencies=self._validate_dependencies,
            debug=debug
        )

    def is_loaded(self) -> bool:
        """判断是否已经加载数据"""
        return self._registry is not None
        
    def _check_loaded(self) -> None:
        if not self.is_loaded():
            raise ServiceNotLoadedError("DefinitionService 尚未加载数据。请先执行 load_from_dir")

    def _check_found(self, obj: Any, kind: str, full_name: str) -> Any:
        if obj is None:
            raise DefinitionNotFoundError(f"未找到对应的 {kind}: {full_name}")
        return obj

    # --- Fetch Methods ---
    def get_entity_set(self, full_name: str) -> Any:
        self._check_loaded()
        assert self._registry is not None
        return self._check_found(self._registry.get_entity_set(full_name), "entity_set", full_name)

    def get_entity_set_link(self, full_name: str) -> Any:
        self._check_loaded()
        assert self._registry is not None
        return self._check_found(self._registry.get_entity_set_link(full_name), "entity_set_link", full_name)

    def get_metric_set(self, full_name: str) -> Any:
        self._check_loaded()
        assert self._registry is not None
        return self._check_found(self._registry.get_metric_set(full_name), "metric_set", full_name)

    def get_log_set(self, full_name: str) -> Any:
        self._check_loaded()
        assert self._registry is not None
        return self._check_found(self._registry.get_log_set(full_name), "log_set", full_name)

    def get_trace_set(self, full_name: str) -> Any:
        self._check_loaded()
        assert self._registry is not None
        return self._check_found(self._registry.get_trace_set(full_name), "trace_set", full_name)
        
    def get_source_file(self, full_name: str) -> Optional[str]:
        self._check_loaded()
        assert self._registry is not None
        return self._registry.get_source_file(full_name)

    # --- List Methods ---
    def list_entity_sets(self) -> List[Any]:
        self._check_loaded()
        assert self._registry is not None
        return self._registry.list_entity_sets()

    def list_entity_set_links(self) -> List[Any]:
        self._check_loaded()
        assert self._registry is not None
        return self._registry.list_entity_set_links()

    def list_metric_sets(self) -> List[Any]:
        self._check_loaded()
        assert self._registry is not None
        return self._registry.list_metric_sets()

    def list_log_sets(self) -> List[Any]:
        self._check_loaded()
        assert self._registry is not None
        return self._registry.list_log_sets()

    def list_trace_sets(self) -> List[Any]:
        self._check_loaded()
        assert self._registry is not None
        return self._registry.list_trace_sets()

    def list_all(self) -> List[Any]:
        self._check_loaded()
        assert self._registry is not None
        return self._registry.list_all()

    # --- Summary ---
    def summary(self) -> Dict[str, Any]:
        """返回当前加载数据的摘要信息"""
        if not self.is_loaded() or self._registry is None:
            return {
                "loaded": False,
                "base_dir": None,
                "total_count": 0
            }

        return {
            "loaded": True,
            "base_dir": str(self._base_dir),
            "entity_set_count": len(self._registry.list_entity_sets()),
            "entity_set_link_count": len(self._registry.list_entity_set_links()),
            "metric_set_count": len(self._registry.list_metric_sets()),
            "log_set_count": len(self._registry.list_log_sets()),
            "trace_set_count": len(self._registry.list_trace_sets()),
            "total_count": len(self._registry.list_all())
        }
