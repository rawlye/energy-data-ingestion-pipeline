from energy_data_ingestion_pipeline.validate import (
    check_project_id_present,
    check_status_allowed,
    validate_record,
)


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
    validation_rows = [
        {"project_id": "SOL-001", "status": "operational"},
        {"project_id": "SOL-001", "status": "Operational"},
        {"project_id": "", "status": "Operational"},
    ]

    assert validate_record(validation_rows[0]) == []
    assert validate_record(validation_rows[1]) == ["status Operational is not allowed"]
    assert validate_record(validation_rows[2]) == [
        "project_id is missing",
        "status Operational is not allowed",
    ]
