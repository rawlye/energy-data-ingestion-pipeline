in bess generator = the energy_mwh is calculated from power_mw and random choice of
hours [1, 2, 4]

commissioning date = if status is operational = it calculates today - 30-3650 days

if status is under construction = today date + 30-365 days
if status is planned = today + 365-1825 days

whether it's "producing"? = if the generated month_start date is on or after
the commissioning date = that means it's already active standing producing project
