from pprint import pprint
from parser.yaml_loader import load_yaml
from parser.registry import parse_definition

path = r"umodel_export/entity_set/acs.entity_set.acs.ack.cluster.yaml"

data = load_yaml(path)

print("type =", type(data))
print("keys =", list(data.keys()))
print("kind =", data.get("kind"))

obj = parse_definition(data)
print("parse success")
print(type(obj))
print(obj)