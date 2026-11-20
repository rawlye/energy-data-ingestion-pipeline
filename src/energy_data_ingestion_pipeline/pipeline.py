from pathlib import Path

from energy_data_ingestion_pipeline.clean import clean_records
from energy_data_ingestion_pipeline.db import get_connection
from energy_data_ingestion_pipeline.extract import extract_records
from energy_data_ingestion_pipeline.load import (
    load_l0_production_plan,
    load_l1_projects,
    load_l1_quarantine,
    load_raw_projects,
)
from energy_data_ingestion_pipeline.validate import validate_records


def run(folder: Path) -> None:
    project_records, plan_records = extract_records(folder)

    with get_connection() as conn:
        loaded_l0_raw = load_raw_projects(conn, project_records)
        loaded_l0_production_plan = load_l0_production_plan(conn, plan_records)
    print(f"L0 project rows loaded: {loaded_l0_raw}")
    print(f"L0 production plan rows loaded: {loaded_l0_production_plan}")

    cleaned_records = clean_records(project_records)

    valid_rows, invalid_rows = validate_records(cleaned_records)

    with get_connection() as conn:
        loaded_l1_rows = load_l1_projects(conn, valid_rows)
        loaded_l1_quarantine = load_l1_quarantine(conn, invalid_rows)
    print(f"L1 rows added: {loaded_l1_rows}")
    print(f"L1 quarantine rows added: {loaded_l1_quarantine}")


if __name__ == "__main__":
    run(Path("data/incoming"))
