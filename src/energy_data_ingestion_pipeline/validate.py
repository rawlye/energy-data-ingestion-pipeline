ALLOWED_STATUSES = [
    "planned",
    "under construction",
    "operational",
]


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


RULES = [check_project_id_present, check_status_allowed]


def validate_record(record: dict) -> list[str]:
    errors_list = []

    for rule in RULES:
        validation_result = rule(record)
        if validation_result is not None:
            errors_list.append(validation_result)
    return errors_list


if __name__ == "__main__":
    validation_rows = [
        {"project_id": "SOL-001", "status": "operational"},
        {"project_id": "", "status": "Operational"},
    ]

    for record in validation_rows:
        print(validate_record(record))
