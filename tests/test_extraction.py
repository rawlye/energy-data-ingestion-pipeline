from pathlib import Path

import pytest
from openpyxl import Workbook

from energy_data_ingestion_pipeline.extract import (
    add_lineage,
    extract_records,
    find_excel_files,
    rows_to_dict,
)


def make_workbook(file_path: Path, sheet_name: str, rows: list[tuple]) -> None:
    workbook = Workbook()
    workbook.remove(workbook["Sheet"])
    sheet = workbook.create_sheet(sheet_name)
    for row in rows:
        sheet.append(row)
    workbook.save(file_path)


def test_finds_only_xlsx_files(tmp_path: Path) -> None:
    (tmp_path / "projects.xlsx").touch()
    (tmp_path / ".DS_Store").touch()
    (tmp_path / "notes.txt").touch()

    result = find_excel_files(tmp_path)

    assert result == [tmp_path / "projects.xlsx"]


def test_returns_files_sorted(tmp_path: Path) -> None:
    (tmp_path / "b.xlsx").touch()
    (tmp_path / "a.xlsx").touch()

    result = find_excel_files(tmp_path)

    assert result == [tmp_path / "a.xlsx", tmp_path / "b.xlsx"]


def test_empty_folder_returns_empty_list(tmp_path: Path) -> None:
    result = find_excel_files(tmp_path)

    assert result == []


def test_missing_folder_raises(tmp_path: Path) -> None:
    missing_folder = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        find_excel_files(missing_folder)


def test_headers_become_keys() -> None:
    list_of_tuples = [("project", "type"), ("SOL-001", "FVE"), ("WIN-01", "Wind")]
    records = rows_to_dict(list_of_tuples)

    assert records == [
        {"project": "SOL-001", "type": "FVE"},
        {"project": "WIN-01", "type": "Wind"},
    ]


def test_sheet_with_only_header_gives_an_empty_list() -> None:
    list_with_only_headers = [("project", "type")]
    records = rows_to_dict(list_with_only_headers)

    assert records == []


def test_lineage() -> None:
    file_name = "projects.xlsx"
    sheet_name = "Projects"
    row = [
        {"project": "SOL-001", "type": "Solar"},
        {"project": "SOL-002", "type": "Solar"},
    ]

    lineage_rows = add_lineage(row, file_name, sheet_name)

    assert lineage_rows == [
        {
            "project": "SOL-001",
            "type": "Solar",
            "source_file": "projects.xlsx",
            "source_sheet": "Projects",
            "source_row": 2,
        },
        {
            "project": "SOL-002",
            "type": "Solar",
            "source_file": "projects.xlsx",
            "source_sheet": "Projects",
            "source_row": 3,
        },
    ]


def test_extracting_records(tmp_path: Path) -> None:

    make_workbook(
        tmp_path / "projects.xlsx",
        "Solar",
        [("project_id", "type"), ("SOL-001", "FVE")],
    )
    make_workbook(
        tmp_path / "production_plan_2026_01.xlsx",
        "Plan",
        [("project_id", "region"), ("SOL-001", "West")],
    )

    projects, plans = extract_records(tmp_path)

    assert projects == [
        {
            "project_id": "SOL-001",
            "type": "FVE",
            "source_file": "projects.xlsx",
            "source_sheet": "Solar",
            "source_row": 2,
        }
    ]

    assert plans == [
        {
            "project_id": "SOL-001",
            "region": "West",
            "source_file": "production_plan_2026_01.xlsx",
            "source_sheet": "Plan",
            "source_row": 2,
        }
    ]


def test_unknown_file_raises_error(tmp_path: Path) -> None:
    make_workbook(
        tmp_path / "budget.xlsx",
        "Budget",
        [("project_id", "region"), ("SOL-001", "West")],
    )

    with pytest.raises(ValueError):
        extract_records(tmp_path)
