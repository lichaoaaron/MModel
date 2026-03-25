import pytest
from pathlib import Path
from services.definition_service import DefinitionService
from parser.errors import ServiceNotLoadedError, DefinitionNotFoundError, DefinitionLoadError
import tempfile
import yaml

@pytest.fixture
def mock_dir(tmp_path):
    entity_dir = tmp_path / "entity_set"
    entity_dir.mkdir()
    
    # Create minimal yaml for entity_set
    es_file = entity_dir / "test_host.yaml"
    es_content = {
        "kind": "entity_set",
        "domain": "test",
        "name": "host",
        "full_name": "test.host",
        "primary_key_fields": ["id"],
        "fields": [{"name": "id", "type": "string"}]
    }
    with open(es_file, "w") as f:
        yaml.dump(es_content, f)

    return tmp_path

def test_service_load_and_summary(mock_dir):
    service = DefinitionService()
    
    assert not service.is_loaded()
    with pytest.raises(ServiceNotLoadedError):
        service.get_entity_set("test.host")
        
    service.load_from_dir(mock_dir, validate_dependencies=True)
    
    assert service.is_loaded()
    
    summary = service.summary()
    assert summary["loaded"] is True
    assert summary["entity_set_count"] == 1
    assert summary["total_count"] == 1

def test_service_get_found_and_not_found(mock_dir):
    service = DefinitionService()
    service.load_from_dir(mock_dir, validate_dependencies=True)
    
    es = service.get_entity_set("test.host")
    assert es.domain == "test"
    assert es.name == "host"
    
    with pytest.raises(DefinitionNotFoundError):
        service.get_entity_set("unknown.entity")
        
    with pytest.raises(DefinitionNotFoundError):
        service.get_metric_set("test.host")

def test_service_reload(mock_dir):
    service = DefinitionService()
    
    with pytest.raises(ServiceNotLoadedError):
        service.reload()
        
    service.load_from_dir(mock_dir, validate_dependencies=True)
    service.reload()
    
    assert service.is_loaded()

def test_service_invalid_load():
    service = DefinitionService()
    with pytest.raises(DefinitionLoadError):
        service.load_from_dir("/invalid/path/that/does/not/exist", validate_dependencies=True)
