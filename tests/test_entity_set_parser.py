import pytest
from model.entity_set import EntitySetDef
from parser.entity_set_parser import parse_entity_set
from parser.entity_set_validator import validate_entity_set_schema
from parser.errors import SchemaValidationError

def get_valid_entity_set_dict() -> dict:
    """生成一个基础的合法 entity_set 字典"""
    return {
        "kind": "entity_set",
        "metadata": {
            "domain": "test_domain",
            "name": "test_entity",
            "display_name": {
                "zh_cn": "测试实体"
            }
        },
        "spec": {
            "id_generator": "snowflake",
            "time_field": "created_at",
            "primary_key_fields": ["id"],
            "fields": [
                {"name": "id", "type": "long"},
                {"name": "name", "type": "string"},
                {"name": "created_at", "type": "long"}
            ]
        }
    }

def test_parse_valid_entity_set():
    """测试合法数据可以成功解析"""
    data = get_valid_entity_set_dict()
    result = parse_entity_set(data)
    
    assert isinstance(result, EntitySetDef)
    assert result.domain == "test_domain"
    assert result.name == "test_entity"
    assert result.full_name == "test_domain.test_entity"
    assert result.id_generator == "snowflake"
    assert len(result.fields) == 3
    assert result.fields[0].name == "id"
    assert result.fields[0].type == "long"

def test_validate_missing_id_generator():
    """测试缺少 spec.id_generator 时校验失败"""
    data = get_valid_entity_set_dict()
    del data["spec"]["id_generator"]
    
    with pytest.raises(SchemaValidationError) as excinfo:
        validate_entity_set_schema(data)
    
    assert "spec.id_generator 必填" in str(excinfo.value)

def test_validate_invalid_time_field():
    """测试 spec.time_field 不在 fields 中时校验失败"""
    data = get_valid_entity_set_dict()
    data["spec"]["time_field"] = "non_existent_field"
    
    with pytest.raises(SchemaValidationError) as excinfo:
        validate_entity_set_schema(data)
    
    assert "spec.time_field 'non_existent_field' 必须存在于 spec.fields 中" in str(excinfo.value)
