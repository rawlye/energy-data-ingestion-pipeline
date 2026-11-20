# Inside pipeline

Flow: extract -> load L0 -> clean -> validate -> load L1 (valid) + quarantine (rejected)

## pipeline.py
- the conductor: calls everything in order
- START HERE when lost

## extract.py
- Excel files -> list of dicts + lineage
- Extracts the data from Excels and adds the source of each row

## load.py
- list of dicts -> DB tables
- writes rows into the database tables: raw rows into L0, valid rows into L1, rejected rows into quarantine

## clean.py
- fixes what's fixable
- strips spaces, puts all status lower-case, etc..

## validate.py
- checks sanity and business rules on the rows
- splits the rows to valid (passed validation) and rejected (failed validation)

## db.py
- creates a connection to the database

## schema.py
- shared constants (statuses, capacity column per type,...)


# Outside pipeline

## generate_data.py
- generates the Excel files with artificial data about projects

## sql/.sql files
- saved SQL scripts which are ran inside DBeaver SQL editor
