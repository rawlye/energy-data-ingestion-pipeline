from datetime import date

from energy_data_ingestion_pipeline.validate import (
    PLAN_RULES,
    PROJECT_RULES,
    check_capacity_positive,
    check_cod_valid,
    check_forecast_version,
    check_plan_month_valid,
    check_planned_energy_mwh,
    check_plans_against_projects,
    check_project_id_present,
    check_project_type,
    check_status_allowed,
    validate_record,
    validate_records,
)

VALID_RECORD = {
    "project_id": "SOL-001",
    "project_type": "Solar",
    "status": "operational",
    "commissioning_date": date(2025, 1, 1),
    "capacity_mwp": 12.5,
}

VALID_PLAN_RECORD = {
    "project_id": "SOL-001",
    "month": date(2026, 3, 1),
    "planned_energy_mwh": 1157.42,
    "forecast_version": 1,
}


def test_check_project_id_present() -> None:
    rows = [{"status": "operational"}, {"project_id": "SOL-001"}, {"project_id": ""}]

    assert check_project_id_present(rows[0]) == "project_id is missing"
    assert check_project_id_present(rows[1]) is None
    assert check_project_id_present(rows[2]) == "project_id is missing"


def test_check_status_allowed() -> None:
    rows = [
        {"status": "operational"},
        {"status": "Operational"},
        {"project_id": "SOL-001"},
    ]

    assert check_status_allowed(rows[0]) is None
    assert check_status_allowed(rows[1]) == "status Operational is not allowed"
    assert check_status_allowed(rows[2]) == "status None is not allowed"


def test_validation_record() -> None:
    wrong_status = VALID_RECORD | {"status": "Operational"}
    wrong_id_and_status = VALID_RECORD | {"project_id": "", "status": "Operational"}

    assert validate_record(VALID_RECORD, PROJECT_RULES) == []
    assert validate_record(wrong_status, PROJECT_RULES) == [
        "status Operational is not allowed"
    ]
    assert validate_record(wrong_id_and_status, PROJECT_RULES) == [
        "project_id is missing",
        "status Operational is not allowed",
    ]


def test_validate_records() -> None:
    wrong_status = VALID_RECORD | {"status": "Operational"}
    wrong_id_and_status = VALID_RECORD | {"project_id": "", "status": "Operational"}
    rows = [VALID_RECORD, wrong_id_and_status, wrong_status]

    valid_rows, invalid_rows = validate_records(rows, PROJECT_RULES)

    assert valid_rows == [VALID_RECORD]

    assert invalid_rows == [
        wrong_id_and_status
        | {
            "reject_reason": [
                "project_id is missing",
                "status Operational is not allowed",
            ]
        },
        wrong_status | {"reject_reason": ["status Operational is not allowed"]},
    ]

    assert (
        "reject_reason" not in wrong_status  # checking that the original is untouched
    )


def test_validate_record_uses_the_rule_list_its_given() -> None:
    assert validate_record(VALID_PLAN_RECORD, PLAN_RULES) == []
    assert validate_record(VALID_RECORD, PLAN_RULES) == [
        "month is missing",
        "planned_energy_mwh is missing",
        "forecast_version is missing",
    ]
    assert validate_record(VALID_PLAN_RECORD, PROJECT_RULES) == [
        "status None is not allowed",
        "project_type is missing",
        "commissioning_date is missing",
    ]


def test_check_wrong_capacity_is_rejected() -> None:
    records = [
        {"project_type": "Solar", "capacity_mwp": 12.5},
        {"project_type": "Wind", "capacity_mw": -5},
        {"project_type": "Solar"},
        {"project_type": "Aero", "capacity_mw": 6},
        {"project_type": "Solar", "capacity_mwp": "n/a"},
    ]

    assert check_capacity_positive(records[0]) is None
    assert check_capacity_positive(records[1]) == "capacity_mw must be > 0, got -5"
    assert check_capacity_positive(records[2]) == "capacity_mwp is missing"
    assert check_capacity_positive(records[3]) is None
    assert check_capacity_positive(records[4]) == "capacity_mwp is not a number"


def test_cod_rules() -> None:
    cod_none = {"project_id": "SOL-001"}
    cod_no_date = {"project_id": "SOL-001", "commissioning_date": "n/a"}
    cod_wrong_date = {"project_id": "SOL-001", "commissioning_date": date(2051, 1, 1)}
    cod_2050_date = {"project_id": "SOL-001", "commissioning_date": date(2050, 1, 1)}

    assert check_cod_valid(cod_none) == "commissioning_date is missing"
    assert check_cod_valid(cod_no_date) == "commissioning_date is not a date: n/a"
    assert (
        check_cod_valid(cod_wrong_date)
        == "commissioning_date outside the sanity year range 2000-2050: 2051"
    )
    assert check_cod_valid(VALID_RECORD) is None
    assert check_cod_valid(cod_2050_date) is None


def test_plan_month_check_returns_correct_validation() -> None:
    months = [
        {"project_id": "SOL-001", "month": date(2025, 1, 1)},
        {"project_id": "SOL-002", "month": date(2025, 1, 4)},
        {"project_id": "SOL-003", "month": "2025-01-01"},
        {"project_id": "SOL-004"},
    ]

    assert check_plan_month_valid(months[0]) is None
    assert (
        check_plan_month_valid(months[1])
        == "month is not the 1st day of the month: 2025-01-04"
    )
    assert check_plan_month_valid(months[2]) == "month is not a date: 2025-01-01"
    assert check_plan_month_valid(months[3]) == "month is missing"


def test_check_planned_energy_correctness() -> None:
    planned_energy = [
        {"project_id": "SOL-001", "planned_energy_mwh": 12.4},
        {"project_id": "SOL-001", "planned_energy_mwh": "n/a"},
        {"project_id": "SOL-001"},
        {"project_id": "SOL-001", "planned_energy_mwh": -12.4},
        {"project_id": "SOL-001", "planned_energy_mwh": 0},
    ]

    assert check_planned_energy_mwh(planned_energy[0]) is None
    assert (
        check_planned_energy_mwh(planned_energy[1])
        == "planned_energy_mwh is not a number: n/a"
    )
    assert (
        check_planned_energy_mwh(planned_energy[2]) == "planned_energy_mwh is missing"
    )
    assert (
        check_planned_energy_mwh(planned_energy[3])
        == "planned_energy_mwh is negative number: -12.4"
    )
    assert check_planned_energy_mwh(planned_energy[4]) is None


def test_forecast_version_returns_correct_validation() -> None:
    forecast_version = [
        {"project_id": "SOL-001", "forecast_version": 1},
        {"project_id": "SOL-001"},
        {"project_id": "SOL-001", "forecast_version": "n/a"},
        {"project_id": "SOL-001", "forecast_version": 0},
    ]

    assert check_forecast_version(forecast_version[0]) is None
    assert check_forecast_version(forecast_version[1]) == "forecast_version is missing"
    assert (
        check_forecast_version(forecast_version[2])
        == "forecast_version is invalid format: n/a"
    )
    assert (
        check_forecast_version(forecast_version[3])
        == "forecast_version can't be negative or 0: 0"
    )


def test_check_project_type_returns_correct_validation() -> None:
    records = [
        {"project_id": "SOL-001", "project_type": "Solar"},
        {"project_id": "SOL-001"},
        {"project_id": "SOL-001", "project_type": "Aero"},
    ]

    assert check_project_type(records[0]) is None
    assert check_project_type(records[1]) == "project_type is missing"
    assert check_project_type(records[2]) == "project_type is invalid: Aero"


def test_plans_are_correctly_evaluated_against_actual_projects() -> None:
    plans = [
        {"project_id": "SOL-001"},
        {"project_id": "SOL-999"},
        {"project_id": "WND-003"},
    ]
    valid_projects = [{"project_id": "SOL-001"}]
    rejected_projects = [{"project_id": "WND-003"}]

    good_plans, bad_plans = check_plans_against_projects(
        plans, valid_projects, rejected_projects
    )

    expected_good_plans = [{"project_id": "SOL-001"}]
    expected_bad_plans = [
        {
            "project_id": "SOL-999",
            "reject_reason": ["project_id doesn't exist in project rows: SOL-999"],
        },
        {
            "project_id": "WND-003",
            "reject_reason": ["project_id is in rejected project rows: WND-003"],
        },
    ]

    assert good_plans == expected_good_plans
    assert bad_plans == expected_bad_plans
