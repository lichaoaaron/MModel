from typing import Any, List, Dict
from pathlib import Path

from registry.definition_registry import DefinitionRegistry
from parser.errors import CrossFileValidationError


class DependencyValidator:
    """跨文件依赖校验器"""

    def __init__(self, registry: DefinitionRegistry):
        self.registry = registry
        self.errors: List[Dict[str, Any]] = []

    def _add_error(
        self,
        error_type: str,
        message: str,
        full_name: str | None = None,
        source_file: str | None = None,
    ) -> None:
        self.errors.append(
            {
                "error_type": error_type,
                "message": message,
                "full_name": full_name,
                "source_file": source_file,
            }
        )

    def validate_all(self) -> None:
        """执行所有校验阶段"""
        self.errors.clear()

        # 1. 全局及实体集合基本检查
        self._validate_global_basics()

        # 2. kind 与源文件目录的一致性校验
        self._validate_kind_directory_consistency()

        # 3. entity_set_link 的 src/dest 依赖校验
        self._validate_entity_set_links()

        if self.errors:
            raise CrossFileValidationError(self.errors)

    def _validate_global_basics(self) -> None:
        """全局基础检查：full_name 格式及实体集合基本配置"""
        for kind, store in self.registry._store_map.items():
            for full_name, definition in store.items():
                source_file = self.registry.get_source_file(full_name)

                if not full_name or not isinstance(full_name, str):
                    self._add_error(
                        "InvalidFullName",
                        f"定义的 full_name 为空或无效: {full_name}",
                        full_name,
                        source_file,
                    )
                elif "." not in full_name:
                    self._add_error(
                        "InvalidFullName",
                        f"定义的 full_name 推荐为 'domain.name' 格式: {full_name}",
                        full_name,
                        source_file,
                    )

                if kind == "entity_set":
                    fields = getattr(definition, "fields", None)
                    if not fields:
                        self._add_error(
                            "MissingFields",
                            "entity_set 必须包含至少一个 field",
                            full_name,
                            source_file,
                        )

                    pk_fields = getattr(definition, "primary_key_fields", None)
                    if not pk_fields:
                        self._add_error(
                            "MissingPrimaryKey",
                            "entity_set 必须指定 primary_key_fields",
                            full_name,
                            source_file,
                        )

    def _validate_kind_directory_consistency(self) -> None:
        """轻量级目录一致性校验：definition.kind == 所在目录名"""
        for full_name, source_file in self.registry._source_files.items():
            if not source_file:
                continue

            obj = self._get_obj_by_full_name(full_name)
            if not obj:
                continue

            kind = getattr(obj, "kind", None)
            if not kind:
                continue

            parent_dir = Path(source_file).parent.name

            if kind != parent_dir:
                expected_dirs = [
                    "entity_set",
                    "entity_set_link",
                    "metric_set",
                    "log_set",
                    "trace_set",
                ]
                if parent_dir in expected_dirs:
                    self._add_error(
                        error_type="KindDirectoryMismatch",
                        message=f"定义的 kind '{kind}' 与其所在目录 '{parent_dir}' 不一致",
                        full_name=full_name,
                        source_file=source_file,
                    )

    def _get_obj_by_full_name(self, full_name: str) -> Any:
        for store in self.registry._store_map.values():
            if full_name in store:
                return store[full_name]
        return None

    def _extract_link_endpoint_full_name(self, endpoint: Any) -> str:
        """从 link endpoint 中提取被引用实体名"""
        if not endpoint:
            return ""

        if isinstance(endpoint, str):
            return endpoint.strip()

        if isinstance(endpoint, dict):
            value = (
                endpoint.get("full_name")
                or endpoint.get("name")
                or endpoint.get("entity_set")
                or endpoint.get("source")
                or endpoint.get("target")
                or endpoint.get("src_entity_set")
                or endpoint.get("dest_entity_set")
                or endpoint.get("metadata")
                or ""
            )
            return value.strip() if isinstance(value, str) else ""

        full_name_attr = getattr(endpoint, "full_name", None)
        if isinstance(full_name_attr, str) and full_name_attr.strip():
            return full_name_attr.strip()

        name_attr = getattr(endpoint, "name", None)
        if isinstance(name_attr, str) and name_attr.strip():
            return name_attr.strip()

        entity_set_attr = getattr(endpoint, "entity_set", None)
        if isinstance(entity_set_attr, str) and entity_set_attr.strip():
            return entity_set_attr.strip()

        source_attr = getattr(endpoint, "source", None)
        if isinstance(source_attr, str) and source_attr.strip():
            return source_attr.strip()

        target_attr = getattr(endpoint, "target", None)
        if isinstance(target_attr, str) and target_attr.strip():
            return target_attr.strip()

        src_entity_set_attr = getattr(endpoint, "src_entity_set", None)
        if isinstance(src_entity_set_attr, str) and src_entity_set_attr.strip():
            return src_entity_set_attr.strip()

        dest_entity_set_attr = getattr(endpoint, "dest_entity_set", None)
        if isinstance(dest_entity_set_attr, str) and dest_entity_set_attr.strip():
            return dest_entity_set_attr.strip()

        metadata_attr = getattr(endpoint, "metadata", None)
        if isinstance(metadata_attr, str) and metadata_attr.strip():
            return metadata_attr.strip()

        return ""

    def _validate_entity_set_links(self) -> None:
        """校验 entity_set_link 的 src/dest 引用是否存在"""
        for link in self.registry.list_entity_set_links():
            full_name = self.registry._get_full_name(link)
            source_file = self.registry.get_source_file(full_name)
            
            src_full_name = ""
            dest_full_name = ""

            # Check src_kind and dest_kind first if they exist
            src_kind = getattr(link, "src_kind", None)
            if src_kind and src_kind != "entity_set":
                self._add_error(
                    error_type="InvalidLinkSourceKind",
                    message=f"src_kind must be 'entity_set', got '{src_kind}'",
                    full_name=full_name,
                    source_file=source_file,
                )

            dest_kind = getattr(link, "dest_kind", None)
            if dest_kind and dest_kind != "entity_set":
                self._add_error(
                    error_type="InvalidLinkDestKind",
                    message=f"dest_kind must be 'entity_set', got '{dest_kind}'",
                    full_name=full_name,
                    source_file=source_file,
                )

            # Try to extract true fields first from real link structure
            src_domain = getattr(link, "src_domain", None)
            src_name = getattr(link, "src_name", None)
            if src_domain and src_name:
                if "." in src_name:
                    src_full_name = src_name
                else:
                    src_full_name = f"{src_domain}.{src_name}"
            
            dest_domain = getattr(link, "dest_domain", None)
            dest_name = getattr(link, "dest_name", None)
            if dest_domain and dest_name:
                if "." in dest_name:
                    dest_full_name = dest_name
                else:
                    dest_full_name = f"{dest_domain}.{dest_name}"

            # Fallback to older nested extraction logical paths
            if not src_full_name:
                src_full_name = self._extract_link_endpoint_full_name(
                    getattr(link, "src", None)
                )
            if not dest_full_name:
                dest_full_name = self._extract_link_endpoint_full_name(
                    getattr(link, "dest", None)
                )

            # 2. spec.src / spec.dest
            if not src_full_name or not dest_full_name:
                spec = getattr(link, "spec", None)
                if isinstance(spec, dict):
                    if not src_full_name:
                        src_full_name = self._extract_link_endpoint_full_name(
                            spec.get("src")
                        )
                    if not dest_full_name:
                        dest_full_name = self._extract_link_endpoint_full_name(
                            spec.get("dest")
                        )
                elif spec is not None:
                    if not src_full_name:
                        src_full_name = self._extract_link_endpoint_full_name(
                            getattr(spec, "src", None)
                        )
                    if not dest_full_name:
                        dest_full_name = self._extract_link_endpoint_full_name(
                            getattr(spec, "dest", None)
                        )

            # 3. 兼容拍平字段
            if not src_full_name:
                src_full_name = self._extract_link_endpoint_full_name(
                    getattr(link, "src_full_name", None)
                    or getattr(link, "source_full_name", None)
                )
            if not dest_full_name:
                dest_full_name = self._extract_link_endpoint_full_name(
                    getattr(link, "dest_full_name", None)
                    or getattr(link, "target_full_name", None)
                )

            # 校验 src
            if not src_full_name:
                fields = list(getattr(link, "__dict__", {}).keys())
                self._add_error(
                    error_type="MissingLinkSource",
                    message=f"cannot extract src reference from entity_set_link. Fields: {fields}",
                    full_name=full_name,
                    source_file=source_file,
                )
            elif not self.registry.has_entity_set(src_full_name):
                self._add_error(
                    error_type="MissingLinkSourceTarget",
                    message=f"src not found: {src_full_name}",
                    full_name=full_name,
                    source_file=source_file,
                )

            # 校验 dest
            if not dest_full_name:
                fields = list(getattr(link, "__dict__", {}).keys())
                self._add_error(
                    error_type="MissingLinkDest",
                    message=f"cannot extract dest reference from entity_set_link. Fields: {fields}",
                    full_name=full_name,
                    source_file=source_file,
                )
            elif not self.registry.has_entity_set(dest_full_name):
                self._add_error(
                    error_type="MissingLinkDestTarget",
                    message=f"dest not found: {dest_full_name}",
                    full_name=full_name,
                    source_file=source_file,
                )