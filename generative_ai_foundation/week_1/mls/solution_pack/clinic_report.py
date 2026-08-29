"""Clinic spend summary report.

Reads appointment data and prints visits, spend, and share by category.
"""

from clinic_tracker import VALID_CATEGORIES, load, total_by_category


def build_report(file_path="appointments_sample.csv"):
    # Read appointments from the sample CSV file.
    appointments = load(file_path)

    # Get spend totals for all valid categories.
    totals = total_by_category(appointments)

    # Keep a stable output order for readability.
    preferred_order = [
        "Consultation",
        "Diagnostics",
        "Procedure",
        "Follow-up",
        "Pharmacy",
    ]
    categories = [name for name in preferred_order if name in VALID_CATEGORIES]
    extra_categories = sorted(cat for cat in VALID_CATEGORIES if cat not in categories)
    categories.extend(extra_categories)

    # Count visits for each valid category, starting at zero.
    visits = {category: 0 for category in categories}
    for appointment in appointments:
        category = appointment.get("category")
        if category in visits:
            visits[category] += 1

    # Compute grand totals for spend and visits.
    grand_total_spend = sum(totals.get(category, 0.0) for category in categories)
    grand_total_visits = sum(visits.get(category, 0) for category in categories)

    # Print report header.
    print("SPEND SUMMARY")
    print("")
    print("{:<15} {:>7} {:>12} {:>8}".format("Category", "Visits", "Spend", "Share"))

    # Print one line per valid category, even if it has zero activity.
    for category in categories:
        category_visits = visits.get(category, 0)
        category_spend = totals.get(category, 0.0)
        if grand_total_spend > 0:
            share = (category_spend / grand_total_spend) * 100
        else:
            share = 0.0

        print(
            "{:<15} {:>7} {:>12.2f} {:>7.2f}%".format(
                category,
                category_visits,
                category_spend,
                share,
            )
        )

    # Print the grand total line.
    print("{:<15} {:>7} {:>12.2f} {:>8}".format("TOTAL", grand_total_visits, grand_total_spend, "100.00%" if grand_total_spend > 0 else "0.00%"))

    # Name the largest cost driver.
    if categories:
        largest_category = max(categories, key=lambda cat: totals.get(cat, 0.0))
        largest_spend = totals.get(largest_category, 0.0)
    else:
        largest_category = "None"
        largest_spend = 0.0

    print("")
    print("Largest cost driver: {} ({:.2f})".format(largest_category, largest_spend))


if __name__ == "__main__":
    build_report("appointments_sample.csv")
