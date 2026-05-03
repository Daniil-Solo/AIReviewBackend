from dataclasses import dataclass
from pathlib import Path

import jinja2
from bandit.core import config, manager
from bandit import Issue

IGNORED_DIRECTORIES = ["tests", "migrations", "venv", ".venv", "__pycache__"]


@dataclass
class ExampleItem:
    filename: str
    code: str


@dataclass
class IssueGroup:
    test_id: str
    issue_text: str
    severity: str
    examples: list[ExampleItem]


tpl = jinja2.Template("""
# Отчет по Bandit
{%- for group in issue_groups %}

## [{{ group.test_id }}] [{{ group.severity }}] {{ group.issue_text }}
{%- for item in group.examples %}

FILE: {{ item.filename }}
```py
{{ item.code }}
```

{%- endfor %}
{%- endfor %}
""")


class BanditChecker:
    @staticmethod
    def run(project_directory: Path, ignored_directories: list[str] | None = None) -> list[Issue]:
        bandit_config = config.BanditConfig()
        dirs_to_exclude = ignored_directories or IGNORED_DIRECTORIES

        b_mgr = manager.BanditManager(
            bandit_config,
            'file',
            debug=False,
            verbose=False,
            quiet=True
        )

        b_mgr.discover_files(
            [str(project_directory)],
            recursive=True,
            excluded_paths=",".join(dirs_to_exclude)
        )

        b_mgr.run_tests()
        issues: list[Issue] = b_mgr.get_issue_list()
        return issues

    @staticmethod
    def group_issues(issues: list[Issue]) -> list[IssueGroup]:
        groups = {}
        for issue in issues:
            key = issue.test_id, issue.text
            if key not in groups:
                groups[key] = IssueGroup(test_id=issue.test_id, issue_text=issue.text, severity=issue.severity, examples=[])
            item = ExampleItem(
                filename=issue.fname,
                code=issue.get_code(max_lines=1, tabbed=True).strip(),
            )
            groups[key].examples.append(item)
        return list(groups.values())

    @staticmethod
    def get_report(issue_groups: list[IssueGroup]) -> str:
        return tpl.render(issue_groups=issue_groups).strip()

if __name__ == "__main__":
    checker = BanditChecker()
    try:
        items = checker.run(Path(r"C:\Users\user\PycharmProjects\Hack"))
        groups = checker.group_issues(items)
        print(checker.get_report(groups))
    except Exception as e:
        print(f"Ошибка: {type(e)} {e}")