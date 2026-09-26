"""
Verify save and load together.  (Pass 4)

Run it with:   python verify_save_load.py

save and load are built in one pass because neither is useful without the
other. The only check that matters is the round trip: write it out, read it
back, and confirm nothing was lost or quietly changed on the way.

SYNTHETIC DATA ONLY. Never enter real patient information.
"""

from clinic_tracker import add_appointment, load, save, total_by_category

appointments = []
add_appointment(appointments, "PT-001", "2026-08-03", "Consultation", 120.00)
add_appointment(appointments, "PT-002", "2026-08-12", "Consultation", 120.00)

save(appointments, "round_trip.csv")
reopened = load("round_trip.csv")

print("")
print("  saved   :", len(appointments), "appointments")
print("  reopened:", len(reopened), "appointments")
print("  totals match:", total_by_category(appointments) == total_by_category(reopened))
print("  cost came back as a number, not text:", isinstance(reopened[0]["cost"], float))
print("  loading a file that does not exist:", load("no_such_file.csv"))
print("")
print("  All four lines above should read 2, 2, True, True, and [].")
print("")
