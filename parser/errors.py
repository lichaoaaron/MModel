class ParserBaseError(Exception):
    """基础异常类"""
    pass

class YamlLoadError(ParserBaseError):
    """YAML 加载失败（如语法错误）"""
    pass

class SchemaValidationError(ParserBaseError):
    """Schema 校验失败（缺失必填项或类型不符）"""
    pass

class ParseError(ParserBaseError):
    """业务逻辑解析错误（如字段引用不存在）"""
    pass
