import calendar
import random
from datetime import date, timedelta
from pathlib import Path

from openpyxl import Workbook

PLACES = [
    "Brno",
    "Praha",
    "Hodonin",
    "Morava",
    "Ostrava",
    "Karvina",
    "Pardubice",
    "HK",
    "Znojmo",
]
REGIONS = ["North", "South", "East", "West"]
STATUSES = ["planned", "under construction", "operational"]
BESS_DURATION_HOURS = [1, 2, 4]
REFERENCE_DATE = date(2026, 11, 7)


def build_base_project(number: int, id_prefix: str, name_prefix: str) -> dict:
    status = random.choice(STATUSES)
    cod_date = generate_commissioning_date(status=status)

    project = {
        "project_id": f"{id_prefix}-{number:03d}",
        "project_name": f"{name_prefix} {random.choice(PLACES)}",
        "region": random.choice(REGIONS),
        "status": status,
        "commissioning_date": cod_date,
    }

    return project


def generate_solar_projects(count: int) -> list[dict]:
    solar_projects = []

    for i in range(count):
        project = build_base_project(i + 1, "SOL", "Solar Park")
        project["capacity_mwp"] = round(random.uniform(1, 50), 2)
        solar_projects.append(project)
    return solar_projects


def generate_wind_projects(count: int) -> list[dict]:
    wind_projects = []

    for i in range(count):
        project = build_base_project(i + 1, "WND", "Wind Park")
        project["capacity_mw"] = round(random.uniform(5, 150), 2)
        project["turbine_count"] = random.randint(2, 25)
        wind_projects.append(project)
    return wind_projects


def generate_bess_projects(count: int) -> list[dict]:
    bess_projects = []

    for i in range(count):
        random_power_mw = round(random.uniform(5, 100), 2)
        project = build_base_project(i + 1, "BES", "BESS")
        project["power_mw"] = random_power_mw
        project["energy_mwh"] = round(
            random_power_mw * random.choice(BESS_DURATION_HOURS), 2
        )
        bess_projects.append(project)
    return bess_projects


def generate_commissioning_date(status: str) -> date:

    if status == "operational":
        cod = REFERENCE_DATE - timedelta(days=random.randint(30, 3650))
    elif status == "under construction":
        cod = REFERENCE_DATE + timedelta(days=random.randint(30, 365))
    elif status == "planned":
        cod = REFERENCE_DATE + timedelta(days=random.randint(365, 1825))
    else:
        raise ValueError(f"Unknown status: {status}")

    return cod


def write_sheet(workbook: Workbook, title: str, projects: list[dict]) -> None:
    sheet = workbook.create_sheet(title)
    headers = list(projects[0].keys())
    sheet.append(headers)
    for project in projects:
        sheet.append(list(project.values()))


def generate_month_starts(year: int) -> list[date]:
    months = []

    for month in range(1, 13):
        month_start = date(year, month, 1)
        months.append(month_start)

    return months


def is_producing(project: dict, month_start: date) -> bool:
    commissioning_date = project["commissioning_date"]
    is_operating = commissioning_date <= month_start

    return is_operating


def get_capacity_mw(project: dict) -> float:
    if "capacity_mwp" in project:
        return project["capacity_mwp"]
    elif "capacity_mw" in project:
        return project["capacity_mw"]
    elif "power_mw" in project:
        return project["power_mw"]
    else:
        raise ValueError(f"Unknown capacity in {project}")


def hours_in_month(month_start: date) -> int:
    year = month_start.year
    month = month_start.month
    number_of_days = calendar.monthrange(year, month)[1]

    return number_of_days * 24


def generate_production_plan(projects: list[dict], month_start: date) -> list[dict]:
    plan_list = []

    for project in projects:
        if is_producing(project, month_start):
            project_plan = {
                "project_id": project["project_id"],
                "month": month_start,
                "planned_energy_mwh": 100,
                "forecast_version": 1,
            }
            plan_list.append(project_plan)

    return plan_list


if __name__ == "__main__":
    random.seed(42)
    output_dir = Path(__file__).parents[2] / "data" / "incoming"
    output_dir.mkdir(parents=True, exist_ok=True)

    solar_projects = generate_solar_projects(5)
    wind_projects = generate_wind_projects(5)
    bess_projects = generate_bess_projects(5)

    all_projects = solar_projects + wind_projects + bess_projects

    workbook = Workbook()
    workbook.remove(workbook["Sheet"])

    write_sheet(workbook, "Solar", solar_projects)
    write_sheet(workbook, "Wind", wind_projects)
    write_sheet(workbook, "BESS", bess_projects)

    workbook.save(output_dir / "projects.xlsx")

    for month_start in generate_month_starts(2026):
        month_plan = generate_production_plan(all_projects, month_start)

        plan_workbook = Workbook()
        plan_workbook.remove(plan_workbook["Sheet"])

        write_sheet(plan_workbook, "Plan", month_plan)

        file_name = f"production_plan_{month_start.year}_{month_start.month:02d}.xlsx"

        plan_workbook.save(output_dir / file_name)
