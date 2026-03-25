import pytest
import shutil
from pathlib import Path
import yaml
from registry.definition_loader import DefinitionLoader
from registry.definition_registry import DefinitionRegistry
from parser.errors import DefinitionLoadError

@pytest.fixture
def mock_root_dir(tmp_path):
    entity_dir = tmp_path / "entity_set"
    link_dir = tmp_path / "entity_set_link"
    entity_dir.mkdir()
    link_dir.mkdir()

    # Create dummy yamls
    base_es = {
        "kind": "entity_set",
        "domain": "sys",
        "name": "host",
        "full_name": "sys.host",
        "primary_key_fields": ["id"],
        "fields": [{"name": "id", "type": "string"}]
    }
    
    with open(entity_dir / "es1.yaml", "w") as f:
        yaml.dump(base_es, f)
        
    return tmp_path

def test_loader_scans_correctly(mock_root_dir):
    registry = DefinitionLoader.load_from_directory(mock_root_dir, validate_dependencies=True)
    assert isinstance(registry, DefinitionRegistry)
    
    all_defs = registry.list_all()
    assert len(all_defs) == 1
    
    es = registry.get_entity_set("sys.host")
    assert es is not None
    assert getattr(es, "kind") == "entity_set"
    
def test_loader_invalid_directory():
    with pytest.raises(DefinitionLoadError):
        DefinitionLoader.load_from_directory("/path/not/exist")
