# UModel YAML Parser (Day 2)

这是一个用于解析 UModel/MModel `entity_set` YAML 定义的 Python 后端解析器。

## 功能特性
- **YAML 加载**: 支持 `.yaml` 和 `.yml` 文件读取。
- **Schema 校验**: 严格校验 `kind`, `metadata`, `spec` 等必填字段及字段类型。
- **逻辑校验**: 验证 `time_field` 和 `primary_key_fields` 是否在 `fields` 中定义。
- **对象转换**: 自动将字典转换为强类型的 `EntitySetDef` 数据类。

## 目录结构
```text
project/
├─ model/             # 数据模型定义
├─ parser/            # 解析与校验逻辑
├─ tests/             # 自动化测试
├─ main.py            # 运行入口
└─ requirements.txt    # 依赖声明
```

## 快速开始

### 1. 安装依赖
```cmd
pip install -r requirements.txt
```

### 2. 运行解析示例
该命令会读取 `./umodel_export/entity_set/` 目录下的第一个 YAML 文件并输出解析结果。
```cmd
python main.py
```

### 3. 运行测试
```cmd
python -m pytest tests/
python -m tools.batch_test_entity_set
```

## 当前 Day 2 范围
- 仅支持 `entity_set` 的解析与校验。
- 字段类型目前支持：`string`, `int`, `long`, `json`。
- 不包含数据库、Web 服务等额外逻辑。
