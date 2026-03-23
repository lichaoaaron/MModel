import json
import csv
import re
import traceback
from pathlib import Path
from collections import Counter
from dataclasses import asdict

from parser.yaml_loader import load_yaml
from parser.entity_set_parser import parse_entity_set
from parser.errors import ParserBaseError

def standardize_error(msg: str) -> str:
    """
    轻量标准化错误信息，将具体的值替换为占位符，方便聚合。
    示例：spec.time_field 'created_at' -> spec.time_field '<VALUE>'
    """
    # 替换单引号中的具体值
    msg = re.sub(r"'.*?'", "'<VALUE>'", msg)
    # 替换索引数字 [0], [1]
    msg = re.sub(r"\[\d+\]", "[<INDEX>]", msg)
    # 替换末尾的具体字段名（如 pk 校验后的 : xxx）
    if "字段不存在:" in msg:
        msg = msg.split(":")[0] + ": <FIELD>"
    return msg

def run_batch_test():
    data_dir = Path("umodel_export") / "entity_set"
    report_json = Path("entity_set_batch_test_report.json")
    report_csv = Path("entity_set_batch_test_report.csv")

    if not data_dir.exists():
        print(f"错误: 目录不存在 - {data_dir.absolute()}")
        return

    # 1. 扫描所有 YAML 文件 (包括子目录)
    files = sorted(list(data_dir.rglob("*.yaml")) + list(data_dir.rglob("*.yml")))
    total_files = len(files)
    
    if total_files == 0:
        print(f"未在 {data_dir} 及其子目录下找到 YAML 文件")
        return

    results = []
    passed_count = 0
    failed_count = 0
    error_counter = Counter()
    failed_details = []

    print(f"正在扫描并测试 {total_files} 个文件...\n")

    # 2. 逐个测试
    for file_path in files:
        rel_path = file_path.relative_to(data_dir.parent.parent)
        try:
            raw_data = load_yaml(str(file_path))
            parse_entity_set(raw_data)
            
            # 记录成功
            results.append({
                "file_path": str(rel_path),
                "status": "PASS",
                "error_type": "",
                "error_message": ""
            })
            passed_count += 1
            
        except ParserBaseError as e:
            # 记录已知解析异常
            err_msg = str(e)
            err_type = e.__class__.__name__
            std_msg = standardize_error(err_msg)
            
            results.append({
                "file_path": str(rel_path),
                "status": "FAIL",
                "error_type": err_type,
                "error_message": err_msg
            })
            failed_details.append({
                "path": str(rel_path),
                "type": err_type,
                "message": err_msg
            })
            error_counter[std_msg] += 1
            failed_count += 1
            
        except Exception as e:
            # 记录未知系统异常
            err_msg = f"Unexpected: {str(e)}"
            err_type = "RuntimeError"
            
            results.append({
                "file_path": str(rel_path),
                "status": "FAIL",
                "error_type": err_type,
                "error_message": err_msg
            })
            failed_details.append({
                "path": str(rel_path),
                "type": err_type,
                "message": err_msg
            })
            error_counter["Unexpected System Error"] += 1
            failed_count += 1

    # 3. 计算成功率
    success_rate = (passed_count / total_files * 100) if total_files > 0 else 0

    # 4. 终端打印汇总
    print("=" * 10, "Entity Set Batch Test Summary", "=" * 10)
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
        if failed_count > 5:
            print(f"... and {failed_count - 5} more failures.")
        print()

    # 5. 导出 JSON 报告
    full_report = {
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
        json.dump(full_report, f, indent=4, ensure_ascii=False)

    # 6. 导出 CSV 报告
    with open(report_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["file_path", "status", "error_type", "error_message"])
        writer.writeheader()
        writer.writerows(results)

    print(f"报告已生成:")
    print(f"- JSON: {report_json.absolute()}")
    print(f"- CSV : {report_csv.absolute()}")

if __name__ == "__main__":
    run_batch_test()
