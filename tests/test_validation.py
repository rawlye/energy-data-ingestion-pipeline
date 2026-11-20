from datetime import date

from energy_data_ingestion_pipeline.validate import (
    check_capacity_positive,
    check_cod_valid,
    check_plan_month_valid,
    check_project_id_present,
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

    assert validate_record(VALID_RECORD) == []
    assert validate_record(wrong_status) == ["status Operational is not allowed"]
    assert validate_record(wrong_id_and_status) == [
        "project_id is missing",
        "status Operational is not allowed",
    ]


def test_validate_records() -> None:
    wrong_status = VALID_RECORD | {"status": "Operational"}
    wrong_id_and_status = VALID_RECORD | {"project_id": "", "status": "Operational"}
    rows = [VALID_RECORD, wrong_id_and_status, wrong_status]

    valid_rows, invalid_rows = validate_records(rows)

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
