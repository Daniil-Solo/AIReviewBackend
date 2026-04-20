import json
import re
from json import JSONDecodeError

from reserach.constants import MODELS
from reserach.schemas import ModelProjectEstimation, ModelProjectLog
from reserach.utils import get_reference_path, load_records_from_dataset, get_dataset_path, \
    get_criteria_checks_path, get_logs, calculate_cost


def evaluate_models_by_project(project_id: int, model_logs: list[ModelProjectLog]):
    with open(get_reference_path(project_id), "r", encoding="utf-8") as f:
        reference_checks = json.load(f)
    unique_reference_ids = {check["id"] for check in reference_checks}

    for model in MODELS:
        print(f"Processing: {model} project_id={project_id}")
        estimation = ModelProjectEstimation(project_id=project_id, model=model)

        with open(get_criteria_checks_path(project_id, model), "r", encoding="utf-8") as f:
            content = f.read()

        try:
            json.loads(content)
        except JSONDecodeError:
            content = content.strip().strip("`").strip("json")
        try:
            criteria_checks = json.loads(content)

            for check in criteria_checks:
                if type(check["id"]) != int or (type(check["is_passed"]) != bool and check["is_passed"] is not None) or type(
                        check["comment"]) != str:
                    print(f"Invalid type: {check}")
                    estimation.is_correct_criteria_field_type = False
                    break

            for check in criteria_checks:
                if check["comment"] and not bool(re.search(r'[а-яА-ЯёЁ]', check["comment"])):
                    estimation.has_russian_letters = False
                    print(f"Not russian: {check["comment"]}")
                    break

            unique_check_ids = {check["id"] for check in criteria_checks}
            if unique_reference_ids != unique_check_ids:
                print(f"Non equal ids: model={unique_check_ids}, reference={unique_reference_ids}")
                estimation.is_same_ids = False

            if estimation.is_same_ids:
                amount = 0
                for check, reference in zip(criteria_checks, reference_checks):
                    amount += int(check["is_passed"] == reference["is_passed"])
                    if check["is_passed"] != reference["is_passed"]:
                        print("Not passed!")
                        print("Model", check)
                        print("Author", reference)
                estimation.correct_rate = amount / len(criteria_checks)


            log = next(log for log in model_logs if log.model == model and log.project_id == project_id)
            estimation.cost = calculate_cost(model, log.input_tokens, log.output_tokens)

            estimation.speed = log.output_tokens / log.duration

        except JSONDecodeError:
            estimation.is_valid_or_repairable_json = False
            print(f"Non repairable json!")
        finally:
            print(estimation)
            print()

if __name__ == "__main__":
    print("Starting...")
    projects = load_records_from_dataset(get_dataset_path())
    print(f"Loaded {len(projects)} rows from dataset")

    logs = get_logs()

    for project in projects:
        evaluate_models_by_project(project.id, logs)