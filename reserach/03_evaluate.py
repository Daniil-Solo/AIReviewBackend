import json

from reserach.utils import get_criteria_path, get_reference_path

with open(get_criteria_path(1), "r", encoding="utf-8") as f:
    criteria = json.load(f)


with open(get_reference_path(1), "r", encoding="utf-8") as f:
    reference = json.load(f)

print(len(criteria))
print(len(reference))