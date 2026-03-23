import sys
import os
import json
from pathlib import Path
from collections import Counter
from datetime import datetime

# 将项目根目录添加到 python path
sys.path.append(str(Path(__file__).parent.parent))

from parser.yaml_loader import load_yaml
from parser.registry import parse_definition

def batch_test_invalid(target_dir: str, report_path: str):
    root = Path(target_dir)
    if not root.exists():
        print(f"[-] 错误: 负样本目录不存在: {target_dir}")
        return

    yaml_files = list(root.rglob("*.yaml")) + list(root.rglob("*.yml"))
    total = len(yaml_files)
    
    correctly_rejected = []
    unexpected_passed = []
    error_summary = []

    print(f"[*] 开始负样本批量校验")
    print(f"[*] 目录: {target_dir}")
    print(f"[*] 文件总数: {total}\n")

    for f_path in yaml_files:
        rel_path = str(f_path.relative_to(root))
        try:
            # 1. 加载 YAML
            data = load_yaml(str(f_path))
            
            # 2. 尝试解析 (预期应该抛出异常)
            obj = parse_definition(data)
            
            # 3. 如果没抛异常，说明是“误通过” (False Negative)
            unexpected_passed.append({
                "file": rel_path,
                "kind": data.get("kind", "unknown"),
                "name": data.get("name", "unknown")
            })
            print(f"[!] 误通过: {rel_path}")

        except Exception as e:
            # 4. 捕获到异常，说明“正确拦截” (Correctly Rejected)
            err_msg = str(e)
            err_type = type(e).__name__
            
            correctly_rejected.append({
                "file": rel_path,
                "error_type": err_type,
                "message": err_msg
            })
            error_summary.append(err_msg)

    # 统计
    total_rejected = len(correctly_rejected)
    total_passed = len(unexpected_passed)
    rejection_rate = (total_rejected / total * 100) if total > 0 else 0

    print("\n" + "="*50)
    print(f"负样本校验报告")
    print("="*50)
    print(f"Total Files        : {total}")
    print(f"Correctly Rejected : {total_rejected}")
    print(f"Unexpected Passed  : {total_passed}")
    print(f"Rejection Rate     : {rejection_rate:.2f}%")
    print("="*50)

    if error_summary:
        print("\nTop 5 Error Types:")
        for msg, count in Counter(error_summary).most_common(5):
            print(f"- [{count}] {msg}")

    if unexpected_passed:
        print("\nUnexpected Passed Files (Top 10):")
        for item in unexpected_passed[:10]:
            print(f"- {item['file']}")

    # 生成 JSON 报告
    report = {
        "summary": {
            "total": total,
            "correctly_rejected": total_rejected,
            "unexpected_passed": total_passed,
            "rejection_rate": f"{rejection_rate:.2f}%",
            "generated_at": datetime.now().isoformat()
        },
        "unexpected_passed_files": unexpected_passed,
        "top_errors": [{"message": m, "count": c} for m, c in Counter(error_summary).most_common(10)]
    }
    
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n报告已生成: {report_path}")

if __name__ == "__main__":
    # 配置路径
    TARGET_DIR = os.path.join("umodel_export", "test_invalid_20260323")
    
    # 确保输出目录存在
    os.makedirs("output", exist_ok=True)
    REPORT_FILE = os.path.join("output", "invalid_batch_test_report.json")
    
    batch_test_invalid(TARGET_DIR, REPORT_FILE)
