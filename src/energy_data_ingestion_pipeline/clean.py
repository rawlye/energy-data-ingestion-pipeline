def clean_record(record: dict) -> dict:
    row = record.copy()
    if row.get("status") is not None:
        row["status"] = row["status"].strip().lower()

    return row


def clean_records(records: list[dict]) -> list[dict]:
    cleaned_rows = []
    for record in records:
        cleaned_rows.append(clean_record(record))
    return cleaned_rows


if __name__ == "__main__":
    first_record = {"project_id": "SOL-002", "status": " Operational "}
    second_record = {"project_id": "SOL-003"}

    print(clean_record(first_record))
    print(clean_record(second_record))
