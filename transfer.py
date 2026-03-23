import json
import re
import hashlib
from pathlib import Path

import yaml

# ====== 输入输出 ======
input_file = "entity_store_data.json"
output_dir = Path("umodel_export")
output_dir.mkdir(exist_ok=True)

# ====== 可选：只导出这些类型；若想全部导出，设为 None ======
allowed_kinds = None
# allowed_kinds = {"entity_set", "entity_set_link"}

# ====== 工具函数 ======
def safe(s: str) -> str:
    s = str(s)
    s = re.sub(r'[\\/:*?"<>|]', "_", s)   # Windows 非法字符
    s = s.replace(" ", "_")
    s = s.strip("._")
    return s or "unknown"

def build_filename(domain: str, kind: str, name: str, max_base_len: int = 120) -> str:
    base_name = f"{safe(domain)}.{safe(kind)}.{safe(name)}"
    if len(base_name) > max_base_len:
        short_hash = hashlib.md5(base_name.encode("utf-8")).hexdigest()[:8]
        base_name = f"{base_name[:100]}_{short_hash}"
    return f"{base_name}.yaml"

def try_json_loads(s):
    if s in (None, "", "null"):
        return {}
    if isinstance(s, (dict, list)):
        return s
    try:
        return json.loads(s)
    except Exception:
        return {"raw": s}

# ====== 读取输入 ======
with open(input_file, "r", encoding="utf-8") as f:
    raw = json.load(f)

# 兼容两种常见结构：
# 1) 顶层就是 list
# 2) {"code":"200","data":{"data":[...]}}
if isinstance(raw, list):
    rows = raw
else:
    rows = raw["data"]["data"]

count = 0
skipped = 0

for idx, row in enumerate(rows):
    if not isinstance(row, list) or len(row) < 5:
        skipped += 1
        continue

    row_role = row[0]          # node / link
    kind = row[1]              # entity_set / entity_set_link / explorer / ...
    metadata_str = row[2]
    schema_str = row[3]
    spec_str = row[4]
    extra_str = row[5] if len(row) > 5 else "{}"

    if allowed_kinds is not None and kind not in allowed_kinds:
        continue

    metadata = try_json_loads(metadata_str)
    schema = try_json_loads(schema_str)
    spec = try_json_loads(spec_str)
    extra = try_json_loads(extra_str)

    domain = metadata.get("domain", "unknown")
    name = metadata.get("name", f"{kind}_{idx}")

    obj = {
        "kind": kind,
        "metadata": metadata,
        "schema": schema,
        "spec": spec,
    }

    if extra not in ({}, None):
        obj["extra"] = extra

    # 按类型分文件夹
    kind_dir = output_dir / safe(kind)
    kind_dir.mkdir(parents=True, exist_ok=True)

    filename = build_filename(domain, kind, name)
    out_file = kind_dir / filename

    with open(out_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            obj,
            f,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False
        )

    count += 1

print(f"✅ 已导出 {count} 个文件到: {output_dir.resolve()}")
if skipped:
    print(f"⚠️ 跳过异常记录: {skipped} 条")