import sys
import os
from pathlib import Path
from collections import Counter
import json

# 将项目根目录添加到 python path
sys.path.append(str(Path(__file__).parent.parent))

from parser.yaml_loader import load_yaml
from parser.registry import parse_definition

def batch_test_trace_set(target_dir: str):
    root = Path(target_dir)
    if not root.exists():
        print(f"目录不存在: {target_dir}")
        return

    # 确定输出目录
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    report_json = output_dir / "trace_set_batch_test_report.json"

    yaml_files = list(root.rglob("*.yaml")) + list(root.rglob("*.yml"))
    total = len(yaml_files)
    passed = 0
    failed_details = []
    error_msgs = []

    print(f"开始批量校验 TraceSet, 目录: {target_dir}, 文件数: {total}")

    for f_path in yaml_files:
        try:
            data = load_yaml(str(f_path))
            parse_definition(data)
            passed += 1
        except Exception as e:
            err_msg = str(e)
            error_msgs.append(err_msg)
            failed_details.append((f_path.name, err_msg))

    # 统计
    success_rate = (passed / total * 100) if total > 0 else 0
    common_errors = Counter(error_msgs).most_common(5)

    print("\n" + "="*50)
    print(f"测试结果:")
    print(f"Total Files  : {total}")
    print(f"Passed       : {passed}")
    print(f"Failed       : {len(failed_details)}")
    print(f"Success Rate : {success_rate:.2f}%")
    print("="*50)

    if common_errors:
        print("\nTop 5 Error Types:")
        for msg, count in common_errors:
            print(f"- [{count}] {msg}")

    if failed_details:
        print("\nFirst 5 Failed Files:")
        for name, err in failed_details[:5]:
            print(f"- {name}: {err}")

    # 导出报告
    report_data = {
        "summary": {
            "total": total,
            "passed": passed,
            "failed": len(failed_details),
            "success_rate": f"{success_rate:.2f}%"
        },
        "top_errors": [{"message": m, "count": c} for m, c in common_errors],
        "failed_files": [{"file": name, "error": err} for name, err in failed_details]
    }
    with open(report_json, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    print(f"\n报告已生成: {report_json}")

if __name__ == "__main__":
    # 默认扫描 umodel_export/trace_set
    target = os.path.join("umodel_export", "trace_set")
    batch_test_trace_set(target)
