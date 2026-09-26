"""
Hands-on Round 1: Spot the Flaw.

Two versions of the same helper. One is right and one is wrong.

DO NOT RUN THIS YET.

Work in pairs. Using appointments_sample.csv, predict on paper what each
version returns for category "Consultation" BEFORE you run anything.
Then run it and see who was right.

Rule: judge by behaviour and output, not by which code looks nicer.

SYNTHETIC DATA ONLY. Never enter real patient information.
"""

from clinic_tracker import load


def total_for_category_version_a(appointments, category):
    for appointment in appointments:
        if appointment["category"] == category:
            return appointment["cost"]
    return 0.0


def total_for_category_version_b(appointments, category):
    total = 0.0
    for appointment in appointments:
        if appointment["category"] == category:
            total += appointment["cost"]
    return total


appointments = load("appointments_sample.csv")

print("")
print("  Version A ->", total_for_category_version_a(appointments, "Consultation"))
print("  Version B ->", total_for_category_version_b(appointments, "Consultation"))
print("")
print("  Consultation is two visits at 120.00 each. Only one of these is 240.00.")
print("")
