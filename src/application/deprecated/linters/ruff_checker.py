from dataclasses import dataclass
from pathlib import Path
import json
import subprocess


@dataclass
class LintIssue:
    code: str
    message: str
    filename: str



def run_ruff(project_path: Path) -> list[LintIssue]:
    issues = []

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            str(project_path),
            "--output-format=json",
            "--config=./src/application/project/linters/ruff.toml",
        ],
        capture_output=True,
        text=True,
    )

    try:
        data = json.loads(proc.stdout) if proc.stdout.strip() else []
    except json.JSONDecodeError:
        data = []

    if isinstance(data, dict):
        data = [data]
    elif not isinstance(data, list):
        data = []

    for item in data:
        filename = item.get("filename", "")
        code = item.get("code", "")
        message = item.get("message", "")


        issue = LintIssue(
            code=code,
            message=message,
            filename=filename,
        )
        issues.append(issue)

    return issues


def format_snippet(code: str) -> str:
    return f"```\n{code}\n```"


def group_issues(issues: list[LintIssue]) -> dict[str, list[LintIssue]]:
    grouped: dict[str, list[LintIssue]] = {}
    for issue in issues:
        key = issue.code
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(issue)
    return dict(sorted(grouped.items()))


def generate_report(project_path: Path) -> str:
    parts = ["# Отчет по Ruff\n"]

    ruff_issues = run_ruff(project_path)
    grouped = group_issues(ruff_issues)

    for code, issue_list in grouped.items():
        parts.append(f"## {code}\n")

        for issue in issue_list:
            rel_path = Path(issue.filename).relative_to(project_path)
            parts.append(f"File: {rel_path}")
            parts.append(f"Message: {issue.message}")
            parts.append("")
    else:
        parts.append("Нет проблем по текущему конфигу")

    return "\n".join(parts)


def main(path: str, output: str | None = None) -> None:
    project_path = Path(path).resolve()
    markdown = generate_report(project_path)

    if output:
        output_path = Path(output).resolve()
        output_path.write_text(markdown, encoding="utf-8")
    else:
        print(markdown)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m lint_report <project_path> [--output report.md]")
        sys.exit(1)

    path = sys.argv[1]
    output = None

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output = sys.argv[idx + 1]

    main(path, output)
