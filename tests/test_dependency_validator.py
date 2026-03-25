import pytest
import os
from pathlib import Path
from registry.definition_loader import DefinitionLoader
from registry.dependency_validator import DependencyValidator
from parser.errors import CrossFileValidationError

# 尝试利用系统 tmp_path fixture

@pytest.fixture
def mock_registry():
    from registry.definition_registry import DefinitionRegistry
    return DefinitionRegistry()

class DummyEntitySet:
    def __init__(self, full_name, kind="entity_set"):
        self.full_name = full_name
        self.kind = kind
        self.fields = [{"name": "id"}]
        self.primary_key_fields = ["id"]

class DummyLink:
    def __init__(self, full_name, src_name, dest_name, kind="entity_set_link"):
        self.full_name = full_name
        self.kind = kind
        self.src_full_name = src_name
        self.dest_full_name = dest_name

def test_dependency_validator_passes(mock_registry):
    es = DummyEntitySet("host.machine")
    mock_registry.register(es, "entity_set/a.yaml")
    
    link = DummyLink("host.machine_link", "host.machine", "host.machine")
    mock_registry.register(link, "entity_set_link/b.yaml")
    
    validator = DependencyValidator(mock_registry)
    validator.validate_all()
    assert not validator.errors

def test_dependency_validator_link_missing_src(mock_registry):
    link = DummyLink("host.machine_link", "host.machine", "target.missing")
    mock_registry.register(link, "entity_set_link/b.yaml")
    
    validator = DependencyValidator(mock_registry)
    with pytest.raises(CrossFileValidationError) as e:
        validator.validate_all()
        
    err_str = str(e.value)
    # assert "InvalidLinkSource" in err_str or "InvalidLinkDest" in err_str
    assert (
    "MissingLinkSourceTarget" in err_str
    or "MissingLinkDestTarget" in err_str
    or "InvalidLinkSource" in err_str
    or "InvalidLinkDest" in err_str
    )
    assert "target.missing" in err_str

def test_dependency_validator_empty_full_name_and_missing_keys(mock_registry):
    es = DummyEntitySet("bad_name")
    es.primary_key_fields = []
    
    mock_registry.register(es, "entity_set/a.yaml")
    validator = DependencyValidator(mock_registry)
    
    with pytest.raises(CrossFileValidationError) as e:
        validator.validate_all()
        
    err_str = str(e.value)
    assert "MissingPrimaryKey" in err_str
