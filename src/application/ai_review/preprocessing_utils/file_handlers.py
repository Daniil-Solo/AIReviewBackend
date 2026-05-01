from collections.abc import Callable
import csv
from pathlib import Path

from nbconvert import MarkdownExporter
import nbformat
import openpyxl


FileHandler = Callable[[Path], str]


def _notebook_handler(path: Path) -> str:
    with open(path, encoding="utf-8") as f:
        notebook_node = nbformat.read(f, as_version=4)

    notebook_node.cells = [cell for cell in notebook_node.cells if cell.get("source", "").strip() != ""]
    md_exporter = MarkdownExporter()
    md_exporter.exclude_output = True
    content, _ = md_exporter.from_notebook_node(notebook_node)
    return content


def _format_table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    col_widths = [max(len(str(row[i])) for row in rows) for i in range(len(rows[0]))]
    lines = []
    for row in rows:
        line = " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
        lines.append(line)
    return "\n".join(lines)


def _csv_handler(path: Path) -> str:
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        rows = []
        for _ in range(5):
            row = next(reader, None)
            if row is None:
                break
            rows.append(row)
    table = _format_table(rows)
    return f"{table}\n\nПервые 5 строк"


def _excel_handler(path: Path) -> str:
    wb = openpyxl.load_workbook(path, read_only=True)
    ws = wb.active
    rows = [[str(cell.value or "") for cell in row][:5] for row in list(ws.iter_rows(max_row=5))]
    wb.close()
    table = _format_table(rows)
    return f"{table}\n\nПервые 5 строк"


DEFAULT_FILE_HANDLERS: dict[str, FileHandler] = {
    ".ipynb": _notebook_handler,
    ".csv": _csv_handler,
    ".xlsx": _excel_handler,
}
