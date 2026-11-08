from pathlib import Path

import pytest

from energy_data_ingestion_pipeline.extract import find_excel_files


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
