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


if __name__ == "__main__":
    rows = [
        {"status": "operational"},
        {"status": "Operational"},
        {"project_id": "SOL-001"},
    ]

    for row in rows:
        validation_id = check_project_id_present(row)
        validation_status = check_status_allowed(row)
        print(validation_id)
        print(validation_status)
