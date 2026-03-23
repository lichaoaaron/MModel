import json
import csv
import re
from pathlib import Path
from collections import Counter
from parser.yaml_loader import load_yaml
from parser.registry import parse_definition
from parser.errors import ParserBaseError

def standardize_error(msg: str) -> str:
    """标准化错误信息，方便归类聚合"""
    msg = re.sub(r"'.*?'", "'<VALUE>'", msg)
    msg = re.sub(r"\[\d+\]", "[<INDEX>]", msg)
    return msg

def run_batch_test_links():
    # 1. 确定扫描目录
    data_dir = Path("umodel_export") / "entity_set_link"
    report_json = Path("entity_set_link_batch_test_report.json")

    if not data_dir.exists():
        print(f"错误: 目录不存在 - {data_dir.absolute()}")
        return

    # 2. 扫描所有 YAML 文件
    files = sorted(list(data_dir.rglob("*.yaml")) + list(data_dir.rglob("*.yml")))
    total_files = len(files)
    
    if total_files == 0:
        print(f"未在 {data_dir} 目录下找到 .yaml 或 .yml 文件")
        return

    results = []
    passed_count = 0
    failed_count = 0
    error_counter = Counter()
    failed_details = []

    print(f"正在扫描并验证 {total_files} 个 EntitySetLink 文件...\n")

    # 3. 逐个验证
    for file_path in files:
        rel_path = file_path.relative_to(data_dir.parent.parent)
        try:
            raw_data = load_yaml(str(file_path))
            # 使用统一入口 parse_definition，它会自动识别 kind 并调用对应 parser
            parse_definition(raw_data)
            
            passed_count += 1
        except ParserBaseError as e:
            err_msg = str(e)
            std_msg = standardize_error(err_msg)
            
            failed_details.append({
                "path": str(rel_path),
                "type": e.__class__.__name__,
                "message": err_msg
            })
            error_counter[std_msg] += 1
            failed_count += 1
        except Exception as e:
            err_msg = f"Unexpected: {str(e)}"
            failed_details.append({
                "path": str(rel_path),
                "type": "RuntimeError",
                "message": err_msg
            })
            error_counter["Unexpected System Error"] += 1
            failed_count += 1

    # 4. 终端输出汇总
    success_rate = (passed_count / total_files * 100) if total_files > 0 else 0

    print("=" * 10, "Entity Set Link Batch Test Summary", "=" * 10)
    print(f"Total Files  : {total_files}")
    print(f"Passed       : {passed_count}")
    print(f"Failed       : {failed_count}")
    print(f"Success Rate : {success_rate:.2f}%")
    print()

    if failed_count > 0:
        print("=" * 10, "Top Errors (Standardized)", "=" * 10)
        for i, (msg, count) in enumerate(error_counter.most_common(10), 1):
            print(f"{i}. {msg} -> {count}")
        print()

        print("=" * 10, "Failed Files Detail (First 5)", "=" * 10)
        for i, detail in enumerate(failed_details[:5], 1):
            print(f"[{i}] {detail['path']}")
            print(f"    Type: {detail['type']}")
            print(f"    Msg : {detail['message']}")
        print()

    # 5. 导出 JSON 报告方便排查
    report_data = {
        "summary": {
            "total": total_files,
            "passed": passed_count,
            "failed": failed_count,
            "success_rate": f"{success_rate:.2f}%"
        },
        "grouped_errors": dict(error_counter),
        "failed_files": failed_details
    }
    with open(report_json, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=4, ensure_ascii=False)

    print(f"详细报告已生成至: {report_json.absolute()}")

if __name__ == "__main__":
    run_batch_test_links()
