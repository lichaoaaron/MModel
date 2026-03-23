import yaml
import os
from .errors import YamlLoadError

def load_yaml(path: str) -> dict:
    """
    加载 YAML 文件并返回字典内容。
    
    Args:
        path: YAML 文件路径
        
    Returns:
        dict: YAML 解析后的内容
        
    Raises:
        YamlLoadError: 文件不存在、语法错误或格式非字典时抛出
    """
    if not os.path.exists(path):
        raise YamlLoadError(f"YAML 文件不存在: {path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise YamlLoadError(f"YAML 语法错误 ({path}): {str(e)}")
    except Exception as e:
        raise YamlLoadError(f"无法读取文件 ({path}): {str(e)}")
        
    if not isinstance(data, dict):
        raise YamlLoadError(f"YAML 顶层格式错误，应为 dict ({path})")
        
    return data
