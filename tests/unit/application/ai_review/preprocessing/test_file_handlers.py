import openpyxl
from src.application.ai_review.preprocessing_utils.file_handlers import (
    DEFAULT_FILE_HANDLERS,
    _csv_handler,
    _excel_handler,
    _format_table,
)


def test__format_table__empty():
    result = _format_table([])
    assert result == ""

def test__format_table__single_row():
    rows = [["a", "b", "c"]]
    result = _format_table(rows)
    assert "a" in result
    assert "b" in result
    assert "c" in result

def test__format_table__multiple_rows():
    rows = [
        ["name", "age"],
        ["Alice", "25"],
        ["Bob", "30"],
    ]
    result = _format_table(rows)
    assert "name" in result
    assert "age" in result
    assert "Alice" in result
    assert "Bob" in result


def test__csv_handler__reads_first_five_rows(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("a,b,c\n1,2,3\n4,5,6\n7,8,9\n10,11,12\n13,14,15")

    result = _csv_handler(csv_file)

    assert "a" in result
    assert "b" in result
    assert "c" in result
    assert "1" in result
    assert "Первые 5 строк" in result
    assert "13" not in result

def test__csv_handler__less_than_five_rows(tmp_path):
    csv_file = tmp_path / "small.csv"
    csv_file.write_text("x,y\n1,2\n3,4")

    result = _csv_handler(csv_file)

    assert "x" in result
    assert "y" in result
    assert "1" in result
    assert "2" in result
    assert "Первые 5 строк" in result

def test__csv_handler__adds_footnote(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("col1,col2\nval1,val2\nval3,val4")

    result = _csv_handler(csv_file)

    assert result.endswith("Первые 5 строк")


def test__excel_handler__reads_first_five_rows(tmp_path):
    xlsx_file = tmp_path / "data.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["name", "age", "city"])
    ws.append(["Alice", "25", "Moscow"])
    ws.append(["Bob", "30", "SPB"])
    ws.append(["Charlie", "35", "Novosibirsk"])
    ws.append(["Diana", "40", "Kazan"])
    ws.append(["Egor", "45", "Ekaterinburg"])
    wb.save(xlsx_file)

    result = _excel_handler(xlsx_file)

    assert "name" in result
    assert "age" in result
    assert "city" in result
    assert "Alice" in result
    assert "Первые 5 строк" in result
    assert "Egor" not in result

def test__excel_handler__adds_footnote(tmp_path):
    xlsx_file = tmp_path / "data.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["col1", "col2"])
    ws.append(["v1", "v2"])
    wb.save(xlsx_file)

    result = _excel_handler(xlsx_file)

    assert "Первые 5 строк" in result


def test__csv_handler_registered():
    assert ".csv" in DEFAULT_FILE_HANDLERS
    assert DEFAULT_FILE_HANDLERS[".csv"] == _csv_handler

def test__excel_handler_registered():
    assert ".xlsx" in DEFAULT_FILE_HANDLERS
    assert DEFAULT_FILE_HANDLERS[".xlsx"] == _excel_handler

def test__notebook_handler_still_registered():
    assert ".ipynb" in DEFAULT_FILE_HANDLERS
