import sys
import json
from pathlib import Path
from services.definition_service import DefinitionService
from parser.errors import ParserBaseError

def main():
    service = DefinitionService()
    
    data_dir = "umodel_export"
    print(f"--- 1. 开始加载数据: {data_dir} ---")
    try:
        service.load_from_dir(data_dir, validate_dependencies=True, debug=True)
        print("加载及依赖校验成功！\n")
    except Exception as e:
        print(f"加载失败:\n{e}")
        return
        
    print("--- 2. 打印 Summary ---")
    summary = service.summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print()
    
    print("--- 3. 读取并展示部分数据 ---")
    entity_sets = service.list_entity_sets()
    print(f"共有 {len(entity_sets)} 个 Entity Set。")
    if entity_sets:
        # 尝试读取第一个 entity_set
        first_es = entity_sets[0]
        full_name = getattr(first_es, "full_name", None) or f"{first_es.domain}.{first_es.name}"
        print(f"\n准备读取: {full_name}")
        
        try:
            es_obj = service.get_entity_set(full_name)
            print(f"成功通过 service 读取到对象！对象包含的字段数: {len(es_obj.fields)}")
            print(f"文件来源: {service.get_source_file(full_name)}")
        except Exception as e:
            print(f"读取失败: {e}")
            
    print("\n--- 4. 列出所有 Entity Set Full Name ---")
    for es in entity_sets[:5]: # 只列出前5个示例
         fname = getattr(es, "full_name", None) or f"{es.domain}.{es.name}"
         print(f"- {fname}")
    if len(entity_sets) > 5:
         print("...")

if __name__ == "__main__":
    main()
