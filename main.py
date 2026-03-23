import sys
from pathlib import Path
from parser.yaml_loader import load_yaml
from parser.entity_set_parser import parse_entity_set
from parser.errors import ParserBaseError

def main():
    # 1. 确定数据目录 (相对路径兼容 Windows)
    data_dir = Path("umodel_export") / "entity_set"
    
    if not data_dir.exists():
        print(f"错误: 目录不存在 - {data_dir.absolute()}")
        return

    # 2. 查找 YAML 文件
    yaml_files = list(data_dir.glob("*.yaml")) + list(data_dir.glob("*.yml"))
    
    if not yaml_files:
        print(f"未在 {data_dir} 目录下找到 .yaml 或 .yml 文件")
        return

    # 3. 取第一个文件进行演示解析
    target_file = yaml_files[0]
    print(f"--- 正在解析: {target_file.name} ---")
    print(f"完整路径: {target_file.absolute()}")

    try:
        # 加载
        raw_data = load_yaml(str(target_file))
        
        # 解析
        entity_set_def = parse_entity_set(raw_data)
        
        # 输出结果
        print("\n[✔] 解析成功!")
        print("-" * 20)
        print(f"Domain: {entity_set_def.domain}")
        print(f"Name: {entity_set_def.name}")
        print(f"Full Name: {entity_set_def.full_name}")
        print(f"ID Generator: {entity_set_def.id_generator}")
        print(f"PK Fields: {entity_set_def.primary_key_fields}")
        print(f"Fields Count: {len(entity_set_def.fields)}")
        print("-" * 20)
        print("对象详情:")
        print(entity_set_def)
        
    except ParserBaseError as e:
        print(f"\n[✘] 解析失败: {e}")
    except Exception as e:
        print(f"\n[!] 发生意外错误: {e}")

if __name__ == "__main__":
    main()
