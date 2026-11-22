from pathlib import Path

from energy_data_ingestion_pipeline.clean import clean_records
from energy_data_ingestion_pipeline.db import get_connection
from energy_data_ingestion_pipeline.extract import extract_records
from energy_data_ingestion_pipeline.load import (
    load_l0_production_plan,
    load_l0_raw_projects,
    load_l1_plans,
    load_l1_projects,
    load_l1_quarantine,
    load_l1_quarantine_plans,
)
from energy_data_ingestion_pipeline.validate import (
    PLAN_RULES,
    PROJECT_RULES,
    check_plans_against_projects,
    validate_records,
)


def run(folder: Path) -> None:
    project_records, plan_records = extract_records(folder)

    with get_connection() as conn:
        loaded_l0_raw = load_l0_raw_projects(conn, project_records)
        loaded_l0_production_plan = load_l0_production_plan(conn, plan_records)
    print(f"L0 project rows loaded: {loaded_l0_raw}")
    print(f"L0 production plan rows loaded: {loaded_l0_production_plan}")

    cleaned_project_records = clean_records(project_records)

    valid_project_rows, invalid_project_rows = validate_records(
        cleaned_project_records, PROJECT_RULES
    )
    valid_plan_rows, invalid_plan_rows = validate_records(plan_records, PLAN_RULES)

    kept_plans, set_aside_plans = check_plans_against_projects(
        valid_plan_rows, valid_project_rows, invalid_project_rows
    )

    invalid_plan_rows.extend(set_aside_plans)

    with get_connection() as conn:
        loaded_l1_rows = load_l1_projects(conn, valid_project_rows)
        loaded_l1_quarantine = load_l1_quarantine(conn, invalid_project_rows)
        loaded_l1_plans = load_l1_plans(conn, kept_plans)
        loaded_l1_plan_quarantine = load_l1_quarantine_plans(conn, invalid_plan_rows)
    print(f"L1 rows added: {loaded_l1_rows}")
    print(f"L1 quarantine rows added: {loaded_l1_quarantine}")
    print(f"L1 plan rows added: {loaded_l1_plans}")
    print(f"L1 plan quarantine rows added: {loaded_l1_plan_quarantine}")


if __name__ == "__main__":
    run(Path("data/incoming"))
