from pathlib import Path

from openpyxl import Workbook, load_workbook


def find_excel_files(folder: Path) -> list[Path]:
    if not folder.is_dir():
        raise FileNotFoundError(f"Path doesn't exist: {folder}")

    xlsx_files = sorted(folder.glob("*.xlsx"))

    return xlsx_files


def read_sheet_rows(workbook: Workbook, sheet_name: str) -> list[tuple]:
    sheet = workbook[sheet_name]
    rows = list(sheet.iter_rows(values_only=True))

    return rows


def rows_to_dict(rows: list[tuple]) -> list[dict]:
    headers = rows[0]
    data_rows = rows[1:]
    result = []

    for one_tuple in data_rows:
        record = {}
        for position in range(len(headers)):
            record[headers[position]] = one_tuple[position]
        result.append(record)

    return result


if __name__ == "__main__":
    incoming_dir = Path(__file__).parents[2] / "data" / "incoming"

    for file_path in find_excel_files(incoming_dir):
        workbook = load_workbook(file_path)

        for sheet_name in workbook.sheetnames:
            rows = read_sheet_rows(workbook, sheet_name)
            records = rows_to_dict(rows)
            print(file_path.name, sheet_name, records[0])
