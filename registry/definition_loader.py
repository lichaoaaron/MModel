from pathlib import Path
from typing import Union
from parser.yaml_loader import load_yaml
from parser.registry import parse_definition
from parser.errors import ParserBaseError, DefinitionLoadError
from .definition_registry import DefinitionRegistry

class DefinitionLoader:
    """定义加载器，负责从目录中扫描、读取并注册定义"""

    # 默认需要扫描的子目录
    TARGET_DIRS = [
        "entity_set",
        "entity_set_link",
        "metric_set",
        "log_set",
        "trace_set"
    ]

    @classmethod
    def load_from_directory(cls, root_dir: Union[str, Path], validate_dependencies: bool = True, debug: bool = False) -> DefinitionRegistry:
        """从指定根目录加载所有定义并返回注册中心"""
        root_path = Path(root_dir)
        if not root_path.exists() or not root_path.is_dir():
            raise DefinitionLoadError(f"定义的根目录不存在或不是一个目录: {root_path.absolute()}")

        registry = DefinitionRegistry()

        for sub_dir_name in cls.TARGET_DIRS:
            target_dir = root_path / sub_dir_name
            if not target_dir.exists() or not target_dir.is_dir():
                continue

            # 扫描目录下的 yml / yaml 文件
            yaml_files = list(target_dir.glob("*.yaml")) + list(target_dir.glob("*.yml"))
            for file_path in yaml_files:
                cls._load_and_register_file(file_path, registry, debug)

        if validate_dependencies:
            from .dependency_validator import DependencyValidator
            validator = DependencyValidator(registry)
            validator.validate_all()

        return registry

    @staticmethod
    def _load_and_register_file(file_path: Path, registry: DefinitionRegistry, debug: bool = False) -> None:
        source_file_str = str(file_path.absolute())
        
        if debug:
            print(f"[DEBUG] Loading file: {source_file_str}")
            
        try:
            # 1. 纯读取 YAML
            raw_data = load_yaml(source_file_str)
            if not raw_data:
                if debug:
                    print(f"[DEBUG] File is empty or returned None: {source_file_str}")
                return

            if debug:
                print(f"[DEBUG] YAML data type: {type(raw_data)}")
                if isinstance(raw_data, dict):
                    print(f"[DEBUG] YAML keys: {list(raw_data.keys())}")
                    print(f"[DEBUG] YAML kind: {raw_data.get('kind')}")

            # 2. 调用统一解析入口
            # 注意: 必须传递完整的原始 raw_data (顶层 dict)
            definition_obj = parse_definition(raw_data)
            
            # 手动注入一个 kind 属性到解析后的对象（以防 parser 返回的对象没有 kind，导致 register 失败）
            if not hasattr(definition_obj, "kind") and isinstance(raw_data, dict) and "kind" in raw_data:
                setattr(definition_obj, "kind", raw_data.get("kind"))

            if debug:
                # 尝试获取解析后的 full_name
                full_name = getattr(definition_obj, "full_name", None)
                if not full_name and hasattr(definition_obj, "domain") and hasattr(definition_obj, "name"):
                    full_name = f"{definition_obj.domain}.{definition_obj.name}"
                print(f"[DEBUG] Parse success, full_name: {full_name}")

            # 3. 注册到中心
            registry.register(definition_obj, source_file=source_file_str)

        except Exception as e:
            # 获取上下文帮助调试
            raw_data_copy = locals().get('raw_data', None)
            context_info = f"File: {source_file_str}\n  Exception Type: {type(e).__name__}\n  Original Error: {str(e)}"
            if raw_data_copy is not None and isinstance(raw_data_copy, dict):
                context_info += f"\n  Keys: {list(raw_data_copy.keys())}\n  Kind: {raw_data_copy.get('kind')}"
                
            raise DefinitionLoadError(f"加载解析失败:\n  {context_info}") from e
