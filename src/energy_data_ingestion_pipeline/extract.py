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


def add_lineage(records: list[dict], file_name: str, sheet_name: str) -> list[dict]:
    records_with_lineage = []

    for position in range(len(records)):
        record_copy = dict(records[position])
        record_copy["source_file"] = file_name
        record_copy["source_sheet"] = sheet_name
        record_copy["source_row"] = position + 2
        records_with_lineage.append(record_copy)
    return records_with_lineage


def extract_records(folder: Path) -> tuple[list[dict], list[dict]]:
    project_records = []
    plan_records = []

    for file_path in find_excel_files(folder):
        workbook = load_workbook(file_path)

        for sheet_name in workbook.sheetnames:
            rows = read_sheet_rows(workbook, sheet_name)
            records = rows_to_dict(rows)
            records_with_lineage = add_lineage(records, file_path.name, sheet_name)
            if file_path.name == "projects.xlsx":
                project_records.extend(records_with_lineage)
            elif file_path.name.startswith("production_plan_"):
                plan_records.extend(records_with_lineage)
            else:
                raise ValueError(f"Unknown file format {file_path.name}")

    return project_records, plan_records


if __name__ == "__main__":
    incoming_dir = Path(__file__).parents[2] / "data" / "incoming"

    project_records, plan_records = extract_records(incoming_dir)
    print(len(project_records), len(plan_records))
