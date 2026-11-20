from datetime import date

from energy_data_ingestion_pipeline.schema import ALLOWED_STATUSES, CAPACITY_FIELDS


def check_project_id_present(record: dict) -> str | None:
    value = record.get("project_id")
    if value is None or value == "":
        return "project_id is missing"
    return None


def check_status_allowed(record: dict) -> str | None:
    status = record.get("status")
    if status not in ALLOWED_STATUSES:
        return f"status {status} is not allowed"
    return None


def check_capacity_positive(record: dict) -> str | None:
    if record.get("project_type") not in CAPACITY_FIELDS:
        return None

    correct_capacity = CAPACITY_FIELDS[record["project_type"]]
    capacity_value = record.get(correct_capacity)

    if capacity_value is None:
        return f"{correct_capacity} is missing"
    elif not isinstance(capacity_value, (int, float)):
        return f"{correct_capacity} is not a number"
    elif capacity_value <= 0:
        return f"{correct_capacity} must be > 0, got {capacity_value}"
    else:
        return None


def check_cod_valid(record: dict) -> str | None:
    cod = record.get("commissioning_date")

    if cod is None:
        return "commissioning_date is missing"
    elif not isinstance(cod, date):
        return f"commissioning_date is not a date: {cod}"
    elif not 2000 <= cod.year <= 2050:
        return f"commissioning_date outside the sanity year range 2000-2050: {cod.year}"
    else:
        return None


RULES = [
    check_project_id_present,
    check_status_allowed,
    check_capacity_positive,
    check_cod_valid,
]


def validate_record(record: dict) -> list[str]:
    errors_list = []

    for rule in RULES:
        validation_result = rule(record)
        if validation_result is not None:
            errors_list.append(validation_result)
    return errors_list


def validate_records(records: list[dict]) -> tuple[list[dict], list[dict]]:
    valid_rows = []
    invalid_rows = []

    for record in records:
        validation_result = validate_record(record)

        if validation_result != []:
            rejected_record = record.copy()
            rejected_record["reject_reason"] = validation_result
            invalid_rows.append(rejected_record)
        else:
            valid_rows.append(record)
    return valid_rows, invalid_rows


if __name__ == "__main__":
    validation_rows = [
        {"project_id": "SOL-001", "status": "operational"},
        {"project_id": "", "status": "Operational"},
        {"project_id": "SOL-001", "status": "Operational"},
        {"project_type": "Solar", "capacity_mwp": 12.5},
        {"project_type": "Wind", "capacity_mw": -5},
        {"project_type": "Solar"},
    ]

    valid_rows, invalid_rows = validate_records(validation_rows)

    print(invalid_rows[0])
