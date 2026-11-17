from pathlib import Path

from energy_data_ingestion_pipeline.clean import clean_records
from energy_data_ingestion_pipeline.extract import extract_records
from energy_data_ingestion_pipeline.validate import validate_records


def run(folder: Path) -> None:
    project_records, _plan_records = extract_records(folder)

    cleaned_records = clean_records(project_records)

    valid_rows, invalid_rows = validate_records(cleaned_records)

    print(f"valid rows: {len(valid_rows)}")
    print(f"invalid rows: {len(invalid_rows)}")

    for row in invalid_rows:
        print(row["source_sheet"], row["source_row"], row["reject_reason"])


if __name__ == "__main__":
    run(Path("data/incoming"))
