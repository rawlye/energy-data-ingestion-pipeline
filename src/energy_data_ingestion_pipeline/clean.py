from energy_data_ingestion_pipeline.schema import CAPACITY_FIELDS


def clean_project_record(record: dict) -> dict:
    row = record.copy()
    if row.get("status") is not None:
        row["status"] = row["status"].strip().lower()

    if row.get("project_type") in CAPACITY_FIELDS:
        correct_capacity = CAPACITY_FIELDS[row["project_type"]]
        capacity_value = row.get(correct_capacity)

        if isinstance(capacity_value, str):
            try:
                capacity_value = float(capacity_value.replace(",", "."))
                row[correct_capacity] = capacity_value
            except ValueError:
                pass  # unfixable text stays as is; validate will reject it later

    return row


def clean_records(records: list[dict]) -> list[dict]:
    cleaned_rows = []
    for record in records:
        cleaned_rows.append(clean_project_record(record))
    return cleaned_rows


if __name__ == "__main__":
    records = [
        {"project_type": "Wind", "capacity_mw": 12.5},
        {"project_type": "Wind", "capacity_mw": "12,5"},
        {"project_type": "Wind", "capacity_mw": "n/a"},
        {"project_type": "Wind"},
    ]

    for record in records:
        print(clean_project_record(record))
