import sys
import os
from pathlib import Path
from collections import Counter

# 将项目根目录添加到 python path
sys.path.append(str(Path(__file__).parent.parent))

from parser.yaml_loader import load_yaml
from parser.registry import parse_definition

def batch_test_metric_set(target_dir: str):
    root = Path(target_dir)
    if not root.exists():
        print(f"目录不存在: {target_dir}")
        return

    yaml_files = list(root.rglob("*.yaml")) + list(root.rglob("*.yml"))
    total = len(yaml_files)
    passed = 0
    failed_details = []
    error_msgs = []

    print(f"开始批量校验 MetricSet, 目录: {target_dir}, 文件数: {total}")

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

if __name__ == "__main__":
    # 默认扫描 umodel_export/metric_set
    target = os.path.join("umodel_export", "metric_set")
    batch_test_metric_set(target)
