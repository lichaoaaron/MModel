class ParserBaseError(Exception):
    """基础异常类"""
    pass

class YamlLoadError(ParserBaseError):
    """YAML 加载/解析基础异常"""
    def __init__(self, message: str, file_path: str | None = None, line: int | None = None):
        self.message = message
        self.file_path = file_path
        self.line = line
        super().__init__(self.message)

class SchemaValidationError(ParserBaseError):
    """Schema 校验失败（缺失必填项或类型不符）"""
    pass

class ParseError(ParserBaseError):
    """业务逻辑解析错误（如字段引用不存在）"""
    pass

class DefinitionRegistryError(ParserBaseError):
    """注册中心基础异常"""
    pass

class DuplicateDefinitionError(DefinitionRegistryError):
    """定义重复异常"""
    pass

class DefinitionLoadError(DefinitionRegistryError):
    """定义加载异常"""
    pass

class DependencyValidationError(ParserBaseError):
    """跨文件依赖校验引发的基础异常"""
    pass

class CrossFileValidationError(DependencyValidationError):
    """跨文件依赖校验失败，聚合多个错误"""
    def __init__(self, errors: list):
        self.errors = errors
        message = f"跨文件依赖校验发现 {len(errors)} 个错误:\n"
        for i, err in enumerate(errors, 1):
            message += f"  [{i}] {err.get('error_type', 'Error')}: {err.get('message', '')} "
            message += f"(full_name: {err.get('full_name', 'N/A')}, file: {err.get('source_file', 'N/A')})\n"
        super().__init__(message)

class DefinitionServiceError(ParserBaseError):
    """对外服务层基础异常"""
    pass

class ServiceNotLoadedError(DefinitionServiceError):
    """定义尚未加载错误"""
    pass

class DefinitionNotFoundError(DefinitionServiceError):
    """未能找到指定定义错误"""
    pass

class ValidationError(ParserBaseError):
    """校验错误"""
    pass
