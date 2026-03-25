import pytest
from registry.definition_registry import DefinitionRegistry
from parser.errors import DuplicateDefinitionError

class DummyDefinition:
    def __init__(self, kind, domain, name):
        self.kind = kind
        self.domain = domain
        self.name = name
        self.full_name = f"{domain}.{name}"

def test_registry_registration_and_retrieval():
    registry = DefinitionRegistry()
    def1 = DummyDefinition("entity_set", "host", "linux")
    registry.register(def1, "mock_source.yaml")
    
    assert registry.has_entity_set("host.linux")
    assert registry.get_entity_set("host.linux") == def1
    assert registry.get_source_file("host.linux") == "mock_source.yaml"

def test_registry_duplicate_registration_fails():
    registry = DefinitionRegistry()
    def1 = DummyDefinition("entity_set", "host", "linux")
    def2 = DummyDefinition("entity_set", "host", "linux")

    registry.register(def1, "mock_source1.yaml")
    with pytest.raises(DuplicateDefinitionError):
        registry.register(def2, "mock_source2.yaml")

def test_registry_unsupported_kind():
    registry = DefinitionRegistry()
    def1 = DummyDefinition("unsupported_set", "host", "linux")
    with pytest.raises(ValueError):
        registry.register(def1)
