"""
Checks for add_appointment.  (Pass 2)

Run it with:   python add_appointment_checks.py

Same style as check_entry_checks.py: each check prints its name, what you
expected, what you got, and PASS or FAIL. No test framework, on purpose.

SYNTHETIC DATA ONLY. Never enter real patient information.
"""

try:
    from clinic_tracker import add_appointment
except ImportError:
    print("")
    print("There is no clinic_tracker.py in this folder yet, or it has no add_appointment piece.")
    print("Build add_appointment first, save it in clinic_tracker.py in this same folder,")
    print("then run this file again.")
    print("")
    raise SystemExit(0)


def run_check(name, expected, got):
    verdict = "PASS" if expected == got else "FAIL"
    print("  {:<40} expected {:<9} got {:<9} {}".format(name, str(expected), str(got), verdict))
    return verdict == "PASS"


print("")
print("CHECKS FOR add_appointment")
print("")

results = []

# normal: a good entry is added
appointments = []
add_appointment(appointments, "PT-001", "2026-08-03", "Consultation", 120.00)
results.append(run_check("a good entry is added", 1, len(appointments)))

# failure: a refused entry must not grow the list
appointments = []
add_appointment(appointments, "PT-001", "2026-08-03", "Consultation", -50)
results.append(run_check("a negative cost is refused", 0, len(appointments)))

# normal: two good entries both survive, in the order they were added
appointments = []
add_appointment(appointments, "PT-001", "2026-08-03", "Consultation", 120.00)
add_appointment(appointments, "PT-002", "2026-08-12", "Consultation", 120.00)
results.append(run_check("two good entries both persist", 2, len(appointments)))
results.append(run_check("the second entry is second", "PT-002", appointments[1]["patient_ref"]))

print("")
print("  {} of {} checks passed.".format(sum(results), len(results)))
print("")
