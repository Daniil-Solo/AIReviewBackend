from dataclasses import dataclass
from pathlib import Path


@dataclass
class DatasetRecord:
    id: int
    repo_url: str
    branch: str
    criteria_path: Path
    reference_path: Path


@dataclass
class ModelProjectLog:
    model: str
    project_id: int
    input_tokens: int
    output_tokens: int
    duration: float


@dataclass
class ModelProjectEstimation:
    model: str
    project_id: int
    is_valid_or_repairable_json: bool = True
    is_correct_criteria_field_type: bool = True
    is_same_ids: bool = True
    has_russian_letters: bool = True
    correct_rate: float | None = None
    cost: float = 0
    speed: float = 0

