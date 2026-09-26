"""
Clinic report outline.

This file holds the reporting part of the tool without implementing it yet.
SYNTHETIC DATA ONLY. Never use real patient information.
"""

from clinic_tracker import VALID_CATEGORIES, load


def build_report(appointments):
    """
    Build a readable spend summary for a clinic manager.
    Shows visits, spend, share by category, and the largest cost driver.
    """
    visits_by_category = {category: 0 for category in VALID_CATEGORIES}
    spend_by_category = {category: 0.0 for category in VALID_CATEGORIES}

    # Count visits and spending from each appointment.
    for appointment in appointments:
        category = appointment["category"]
        cost = float(appointment["cost"])
        visits_by_category[category] += 1
        spend_by_category[category] += cost

    total_visits = sum(visits_by_category.values())
    total_spend = sum(spend_by_category.values())
    has_spend = total_spend != 0

    lines = ["CLINIC SPEND SUMMARY", ""]

    for category in VALID_CATEGORIES:
        visits = visits_by_category[category]
        spend = spend_by_category[category]
        share = (spend / total_spend) * 100 if has_spend else 0.0

        lines.append(
            f"{category}: visits {visits}, spend {spend:.2f}, share {share:.2f}%"
        )

    lines.append("")
    lines.append(f"Total visits: {total_visits}")
    lines.append(f"Total spend: {total_spend:.2f}")

    if has_spend:
        largest_category = max(spend_by_category, key=spend_by_category.get)
        lines.append(
            f"Largest cost driver: {largest_category} "
            f"({spend_by_category[largest_category]:.2f})"
        )
    else:
        lines.append("Largest cost driver: None")

    return "\n".join(lines)


if __name__ == "__main__":
    # Load the sample appointments and print the report when this file is run directly.
    appointments = load("appointments_sample.csv")
    print(build_report(appointments))
