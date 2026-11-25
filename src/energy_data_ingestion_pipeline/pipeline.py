from pathlib import Path

from energy_data_ingestion_pipeline.clean import clean_records
from energy_data_ingestion_pipeline.db import get_connection
from energy_data_ingestion_pipeline.extract import extract_records
from energy_data_ingestion_pipeline.l2 import (
    build_dim_date,
    build_dim_project,
    build_fact_production_plan,
    reset_l2,
)
from energy_data_ingestion_pipeline.load import (
    DATA_COLUMNS,
    INSERT_L0_PRODUCTION_PLAN,
    INSERT_L0_RAW_PROJECT,
    INSERT_L1_PLANS,
    INSERT_L1_PROJECT,
    INSERT_L1_QUARANTINE,
    INSERT_L1_QUARANTINE_PLANS,
    PLAN_COLUMNS,
    load_to_layer,
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
        loaded_l0_raw = load_to_layer(
            conn,
            project_records,
            INSERT_L0_RAW_PROJECT,
            "l0",
            "raw_projects",
            as_text=True,
            with_reason=False,
            columns=DATA_COLUMNS,
        )
        loaded_l0_production_plan = load_to_layer(
            conn,
            plan_records,
            INSERT_L0_PRODUCTION_PLAN,
            "l0",
            "raw_production_plan",
            as_text=True,
            with_reason=False,
            columns=PLAN_COLUMNS,
        )
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
        loaded_l1_rows = load_to_layer(
            conn,
            valid_project_rows,
            INSERT_L1_PROJECT,
            "l1",
            "projects",
            as_text=False,
            with_reason=False,
            columns=DATA_COLUMNS,
        )
        loaded_l1_quarantine = load_to_layer(
            conn,
            invalid_project_rows,
            INSERT_L1_QUARANTINE,
            "l1",
            "quarantine_projects",
            as_text=True,
            with_reason=True,
            columns=DATA_COLUMNS,
        )
        loaded_l1_plans = load_to_layer(
            conn,
            kept_plans,
            INSERT_L1_PLANS,
            "l1",
            "plans",
            as_text=False,
            with_reason=False,
            columns=PLAN_COLUMNS,
        )
        loaded_l1_plan_quarantine = load_to_layer(
            conn,
            invalid_plan_rows,
            INSERT_L1_QUARANTINE_PLANS,
            "l1",
            "quarantine_plans",
            as_text=True,
            with_reason=True,
            columns=PLAN_COLUMNS,
        )
    print(f"L1 rows added: {loaded_l1_rows}")
    print(f"L1 quarantine rows added: {loaded_l1_quarantine}")
    print(f"L1 plan rows added: {loaded_l1_plans}")
    print(f"L1 plan quarantine rows added: {loaded_l1_plan_quarantine}")

    with get_connection() as conn:
        reset_l2(conn)
        loaded_l2_dim_project = build_dim_project(conn)
        loaded_l2_dim_date = build_dim_date(conn)
        loaded_l2_fact_plan = build_fact_production_plan(conn)
    print(f"L2 dim_project rows added: {loaded_l2_dim_project}")
    print(f"L2 dim_date rows added: {loaded_l2_dim_date}")
    print(f"L2 fact_production_plan rows added: {loaded_l2_fact_plan}")


if __name__ == "__main__":
    run(Path("data/incoming"))
