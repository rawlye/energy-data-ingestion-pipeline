from pathlib import Path

from openpyxl import load_workbook


def find_excel_files(folder: Path) -> list[Path]:
    if not folder.is_dir():
        raise FileNotFoundError(f"Path doesn't exist: {folder}")

    xlsx_files = sorted(folder.glob("*.xlsx"))

    return xlsx_files


def get_sheet_names(file_path: Path) -> list[str]:
    workbook = load_workbook(file_path)
    return workbook.sheetnames


if __name__ == "__main__":
    incoming_dir = Path(__file__).parents[2] / "data" / "incoming"
    for file_path in find_excel_files(incoming_dir):
        print(file_path.name)
        print(get_sheet_names(file_path))
