import json
import re
from pathlib import Path
from collections import Counter
from parser.yaml_loader import load_yaml
from parser.registry import parse_definition
from parser.errors import ParserBaseError

def standardize_error(msg: str) -> str:
    msg = re.sub(r"'.*?'", "'<VALUE>'", msg)
    msg = re.sub(r"\[\d+\]", "[<INDEX>]", msg)
    return msg

def run_batch_test_log_set():
    data_dir = Path("umodel_export") / "log_set"
    
    # 修改输出位置到 output/ 文件夹
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    report_json = output_dir / "log_set_batch_test_report.json"

    if not data_dir.exists():
        print(f"错误: 目录不存在 - {data_dir.absolute()}")
        return

    files = sorted(list(data_dir.rglob("*.yaml")) + list(data_dir.rglob("*.yml")))
    total_files = len(files)
    
    if total_files == 0:
        print(f"未在 {data_dir} 目录下找到 YAML 文件")
        return

    passed_count = 0
    failed_count = 0
    error_counter = Counter()
    failed_details = []

    print(f"正在扫描并验证 {total_files} 个 LogSet 文件...\n")

    for file_path in files:
        rel_path = file_path.relative_to(data_dir.parent.parent)
        try:
            raw_data = load_yaml(str(file_path))
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

    success_rate = (passed_count / total_files * 100) if total_files > 0 else 0

    print("=" * 10, "Log Set Batch Test Summary", "=" * 10)
    print(f"Total Files  : {total_files}")
    print(f"Passed       : {passed_count}")
    print(f"Failed       : {failed_count}")
    print(f"Success Rate : {success_rate:.2f}%")
    print()

    if failed_count > 0:
        print("=" * 10, "Top Errors", "=" * 10)
        for i, (msg, count) in enumerate(error_counter.most_common(5), 1):
            print(f"{i}. {msg} -> {count}")
        print()

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
    run_batch_test_log_set()
