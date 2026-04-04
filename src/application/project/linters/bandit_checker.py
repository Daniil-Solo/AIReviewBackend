import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from pprint import pprint
from typing import Any

IGNORED_DIRECTORIES = ["tests", "migrations", "venv", ".venv", "__pycache__"]


@dataclass
class ExampleItem:
    text: str
    severity: str
    filename: str
    line: int
    code: str


@dataclass
class IssueGroup:
    test_name: str
    example_count: int
    examples: list[ExampleItem]


@dataclass
class Statistics:
    low_count: int
    medium_count: int
    high_count: int


class BanditChecker:
    @staticmethod
    def run(project_directory: Path, ignored_directories: list[str] | None = None, timeout: int = 60) -> list[dict[str, Any]]:
        ignored_dirs_string = ",".join(ignored_directories or IGNORED_DIRECTORIES)
        result = subprocess.run(["bandit", str(project_directory), "-r", "-f", "json", f"--exclude={ignored_dirs_string}", "--quiet", "--number=1"], capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            return []

        return json.loads(result.stdout)["results"]

    @staticmethod
    def group_issues(issues: list[dict[str, Any]]) -> list[IssueGroup]:
        data = dict()
        for issue in issues:
            key = issue["test_name"]
            if key not in data:
                group = IssueGroup(test_name=issue["test_name"], example_count=0, examples=[])
                data[key] = group
            item = ExampleItem(
                text=issue["issue_text"],
                severity=issue["issue_severity"],
                filename=issue["filename"],
                line=issue["line_number"],
                code=issue["code"],
            )
            data[key].example_count += 1
            data[key].examples.append(item)
        return list(data.values())

    @staticmethod
    def get_statistics(issues: list[dict[str, Any]]) -> Statistics:
        stats = Statistics(low_count=0, medium_count=0, high_count=0)
        for issue in issues:
            if issue["issue_severity"] == "LOW":
                stats.low_count += 1
            elif issue["issue_severity"] == "MEDIUM":
                stats.medium_count += 1
            elif issue["issue_severity"] == "HIGH":
                stats.high_count += 1
        return stats


checker = BanditChecker()
items = checker.run(Path(r"C:\Users\user\PycharmProjects\pastabean_email_service"))
pprint(checker.group_issues(items))
pprint(checker.get_statistics(items))
