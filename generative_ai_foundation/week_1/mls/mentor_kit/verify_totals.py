"""
Verify total_by_category against the table in project_notes.md.  (Pass 3)

Run it with:   python verify_totals.py

save and load do not exist yet at this point in the session, so the seven
sample rows are entered by hand here. This is the moment you compare the
tool's answer to the 240.00 you wrote on paper before any code existed.

SYNTHETIC DATA ONLY. Never enter real patient information.
"""

from clinic_tracker import add_appointment, total_by_category

appointments = []
add_appointment(appointments, "PT-001", "2026-08-03", "Consultation", 120.00)
add_appointment(appointments, "PT-002", "2026-08-03", "Diagnostics", 340.50)
add_appointment(appointments, "PT-001", "2026-08-10", "Follow-up", 60.00)
add_appointment(appointments, "PT-003", "2026-08-11", "Procedure", 890.00)
add_appointment(appointments, "PT-004", "2026-08-11", "Pharmacy", 15.25)
add_appointment(appointments, "PT-002", "2026-08-12", "Consultation", 120.00)
add_appointment(appointments, "PT-005", "2026-08-12", "Diagnostics", 210.00)

totals = total_by_category(appointments)

print("")
for category, spend in totals.items():
    print("  {:<15} {:>10.2f}".format(category, spend))

print("")
print("  Grand total: {:.2f}".format(sum(totals.values())))
print("  Consultation should be 240.00. Grand total should be 1755.75.")
print("")
print("  An empty list must total to nothing, not crash:")
print("  ", total_by_category([]))
print("")
