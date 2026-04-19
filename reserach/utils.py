import csv
import datetime
from pathlib import Path

from reserach.constants import INPUT_PRICE_MAP, OUTPUT_PRICE_MAP
from reserach.schemas import DatasetRecord
from reserach.settings import RESEARCH_DIR


def get_project_prompt_path(project_id: int) -> Path:
    return  RESEARCH_DIR / "data" / str(project_id) / "project.md"


def get_dataset_path() -> Path:
    return  RESEARCH_DIR / "dataset.csv"


def get_criteria_checks_path(project_id: int, model: str) -> Path:
    if len(model.split("/")) > 1:
        model_name = model.split("/")[-1]
    else:
        model_name = model
    return  RESEARCH_DIR / "answers" / str(project_id) / f"{model_name}.json"

def get_criteria_path(project_id: int) -> Path:
    return  RESEARCH_DIR / "data" / str(project_id) / "criteria.json"


def get_reference_path(project_id: int) -> Path:
    return  RESEARCH_DIR / "data" / str(project_id) / "reference.json"


def load_records_from_dataset(dataset_filepath: Path) -> list[DatasetRecord]:
    records = []
    with open(dataset_filepath, mode='r', newline='') as f:
        csv_reader = csv.reader(f)
        next(csv_reader)
        for row in csv_reader:
            new_record = DatasetRecord(
                id=int(row[0]),
                repo_url=row[1],
                branch=row[2],
                criteria_path=RESEARCH_DIR / row[3],
                reference_path=RESEARCH_DIR / row[4],
            )
            records.append(new_record)
    return records


def log_llm_calling(model: str, project_id: int, input_tokens: int, output_tokens: int, duration: float) -> None:
    log_filepath = RESEARCH_DIR / "log.csv"
    with open(log_filepath, "a+") as f:
        f.write(f"{model},{project_id},{input_tokens},{output_tokens},{duration}\n")


def calculate_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    input_price = INPUT_PRICE_MAP[model_name]
    output_price = OUTPUT_PRICE_MAP[model_name]
    cost = (input_tokens / 1_000_000) * input_price + (output_tokens / 1_000_000) * output_price
    return cost