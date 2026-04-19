from dataclasses import dataclass
from pathlib import Path


@dataclass
class DatasetRecord:
    id: int
    repo_url: str
    branch: str
    criteria_path: Path
    reference_path: Path
