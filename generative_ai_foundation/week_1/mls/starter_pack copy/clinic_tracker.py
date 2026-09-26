"""
Clinic appointment and expense tracker outline.

This file names the main parts of the tool without implementing them yet.
SYNTHETIC DATA ONLY. Never use real patient information.
"""

import csv

# The allowed appointment categories for version 1.
VALID_CATEGORIES = ["Consultation", "Diagnostics", "Procedure", "Follow-up", "Pharmacy"]


def check_entry(patient_ref, date, category, cost):
    """
    Check one appointment before it is added.
    Later this should return the problems found, or an empty result if the entry is valid.
    """
    problems = []

    # A patient reference is required for every appointment.
    if not patient_ref:
        problems.append("Patient reference is missing.")

    # A date is also required.
    if not date:
        problems.append("Date is missing.")

    # Only known clinic categories are allowed.
    if category not in VALID_CATEGORIES:
        problems.append("Unknown category: " + str(category))

    # Cost must be something we can treat as a number.
    try:
        cost_value = float(cost)
    except (TypeError, ValueError):
        problems.append("Cost is not a number.")
        return problems

    # Zero is allowed, but anything below zero is refused.
    if cost_value < 0:
        problems.append("Cost cannot be negative.")

    return problems


def add_appointment(appointments, patient_ref, date, category, cost):
    """
    Add one appointment to the list.
    Refuses invalid entries and adds valid ones to the in-memory list.
    """
    problems = check_entry(patient_ref, date, category, cost)

    # Refuse bad input instead of adding it quietly.
    if problems:
        raise ValueError("; ".join(problems))

    appointment = {
        "patient_ref": patient_ref,
        "date": date,
        "category": category,
        "cost": float(cost),
    }

    appointments.append(appointment)
    return appointments


def total_by_category(appointments):
    """
    Calculate spending totals for each category.
    Returns all categories, including zero totals where no visits exist.
    """
    totals = {}

    # Start every category at zero so missing activity still shows up.
    for category in VALID_CATEGORIES:
        totals[category] = 0.0

    # Add each appointment cost into its category total.
    for appointment in appointments:
        category = appointment["category"]
        totals[category] += float(appointment["cost"])

    return totals


def save(appointments, filename):
    """
    Save the appointment list to a file.
    Writes the current data so the clinic can reopen it later.
    """
    fieldnames = ["patient_ref", "date", "category", "cost"]

    with open(filename, "w", newline="") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=fieldnames)
        writer.writeheader()

        # Write each appointment as one row in the same field order.
        for appointment in appointments:
            writer.writerow({
                "patient_ref": appointment["patient_ref"],
                "date": appointment["date"],
                "category": appointment["category"],
                "cost": "{:.2f}".format(float(appointment["cost"])),
            })


def load(filename):
    """
    Load the appointment list from a file.
    Reads saved data back into the program in the same structure.
    """
    appointments = []

    with open(filename, newline="") as file_handle:
        reader = csv.DictReader(file_handle)

        # Reuse add_appointment so loaded data follows the same rules as new data.
        for row in reader:
            add_appointment(
                appointments,
                row["patient_ref"],
                row["date"],
                row["category"],
                row["cost"],
            )

    return appointments
