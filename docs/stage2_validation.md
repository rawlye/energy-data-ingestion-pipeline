# Stage 2: Validation

## Why it exists
Only data that passes quality and sanity checks may reach the database.
Validation is the first line of defence against invalid or corrupted rows.
Bad rows are not dropped silently: each one is rejected with a reason, and
its lineage (file, sheet, row) shows where it came from.

## Input
A list of records (dicts) from Stage 1 extraction. Example:

    {"project_id": "SOL-001", "project_name": "Solar Park Brno",
     "project_type": "Solar", "region": "East", "status": "operational",
     "commissioning_date": datetime(2025, 7, 9),
     "capacity_mwp": 13,
     "source_file": "projects.xlsx", "source_sheet": "Solar", "source_row": 2}

## Output
Two lists.

### Valid rows
Records that pass every rule, unchanged.

### Rejected rows
The original record plus a `reject_reason` field. Example:

    {"project_id": None, "project_name": "Solar Park Brno", ...,
     "source_file": "projects.xlsx", "source_sheet": "Solar", "source_row": 2,
     "reject_reason": "project_id is missing"}

## Common rules (all sheets)

### project_id
| Check        | Rule |
|--------------|------|
| Required     | reject if empty or None |
| Type         | reject if not a string |
| Format       | `SOL-`, `WND-`, `BES-` or `HYD-` + 3 digits |
| Unique       | yes, within projects.xlsx; reject duplicates |
| Relationship | prefix must match the sheet (`SOL-` only on Solar) |

### project_name
| Check        | Rule |
|--------------|------|
| Required     | reject if empty or None |
| Type         | reject if not a string |
| Unique       | no, duplicates allowed |

### status
| Check          | Rule |
|----------------|------|
| Required       | reject if empty or None |
| Type           | reject if not a string |
| Allowed values | `planned`, `under construction`, `operational` |

### commissioning_date
| Check        | Rule |
|--------------|------|
| Required     | reject if empty or None (the production plan depends on it) |
| Type         | reject if not a date (openpyxl returns `datetime`) |
| Range        | between 2000-01-01 and 2050-12-31 (catches typos like 2206) |
| Relationship | operational → COD must be in the past; planned / under construction → COD must be in the future |

## Solar-only rules

### capacity_mwp
| Check    | Rule |
|----------|------|
| Required | reject if empty or None |
| Type     | reject if not a number (int or float) |
| Range    | must be > 0 |

## Open questions
- Values like `" Operational "` (extra spaces, wrong case): clean them first,
  or reject them?
- Same `project_id` twice with different data: reject both, or keep one?
