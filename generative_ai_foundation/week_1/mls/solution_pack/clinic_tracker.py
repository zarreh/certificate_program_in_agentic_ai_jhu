"""Clinic tracker core pieces.

For now, this file contains check_entry, add_appointment, total_by_category,
and save/load pieces.
"""

import csv
from pathlib import Path

# Valid categories agreed for version 1.
VALID_CATEGORIES = {
    "Consultation",
    "Diagnostics",
    "Procedure",
    "Follow-up",
    "Pharmacy",
}


def _is_missing(value):
    # Missing means None, empty text, or only spaces.
    return value is None or str(value).strip() == ""


def check_entry(patient_ref, date, category, cost):
    """Validate one appointment/expense entry.

    Returns a list of problems. An empty list means the entry is fine.
    """
    problems = []

    # Patient reference is required.
    if _is_missing(patient_ref):
        problems.append("patient_ref is required")

    # Date is required.
    if _is_missing(date):
        problems.append("date is required")

    # Category must be one from the approved list.
    if category not in VALID_CATEGORIES:
        problems.append("category is not valid")

    # Cost must be a number and cannot be negative.
    try:
        numeric_cost = float(cost)
        if numeric_cost < 0:
            problems.append("cost cannot be negative")
    except (TypeError, ValueError):
        problems.append("cost must be a number")

    return problems


def add_appointment(appointments, patient_ref, date, category, cost):
    # Check this entry first using the existing validation rules.
    problems = check_entry(patient_ref, date, category, cost)

    # If there are problems, refuse it by leaving the list unchanged.
    if problems:
        return appointments

    # Entry is valid, so add it to the appointment list.
    appointments.append({
        "patient_ref": patient_ref,
        "date": date,
        "category": category,
        "cost": float(cost),
    })

    # Give the list back, whether changed or unchanged.
    return appointments


def total_by_category(appointments):
    # Start totals at zero for each valid category.
    totals = {
        "Consultation": 0.0,
        "Diagnostics": 0.0,
        "Procedure": 0.0,
        "Follow-up": 0.0,
        "Pharmacy": 0.0,
    }

    # Add each appointment cost into its matching category.
    for appointment in appointments:
        category = appointment.get("category")
        cost = float(appointment.get("cost", 0))

        # Ignore unknown categories in this totals step.
        if category in totals:
            totals[category] += cost

    # Give back total cost per category.
    return totals


def save(appointments, file_path="appointments.csv"):
    # Write all appointments to a CSV file.
    with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["patient_ref", "date", "category", "cost"],
        )
        writer.writeheader()

        for appointment in appointments:
            writer.writerow(
                {
                    "patient_ref": appointment.get("patient_ref", ""),
                    "date": appointment.get("date", ""),
                    "category": appointment.get("category", ""),
                    "cost": appointment.get("cost", 0),
                }
            )


def load(file_path="appointments.csv"):
    # If no file exists yet, return an empty list.
    if not Path(file_path).exists():
        return []

    # Read appointments from CSV and return them as a list.
    appointments = []
    with open(file_path, "r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            appointments.append(
                {
                    "patient_ref": row.get("patient_ref", ""),
                    "date": row.get("date", ""),
                    "category": row.get("category", ""),
                    "cost": float(row.get("cost", 0)),
                }
            )

    return appointments
