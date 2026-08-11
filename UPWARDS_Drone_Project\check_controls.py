"""check_controls.py: test your two functions in controls_lab.py. No drone needed.

    python check_controls.py
"""
from controls_lab import overshoot_percent, settling_time

_passed = 0
_failed = 0


def check(name, got, want):
    global _passed, _failed
    ok = abs(got - want) < 1e-6
    if ok:
        _passed += 1
    else:
        _failed += 1
    print(f"[{'PASS' if ok else 'FAIL'}] {name}   (got {got!r}, want {want!r})")


try:
    overshoot_percent([100, 0])
    settling_time([0, 1], [100, 0])
except NotImplementedError:
    print("Not written yet. Fill in overshoot_percent and settling_time, then run this again.")
    raise SystemExit
except Exception as exc:
    print(f"Something errored: {exc}")
    raise SystemExit

print("Testing overshoot_percent...\n")
check("empty list is 0%", overshoot_percent([]), 0.0)
check("clean decay, no overshoot", overshoot_percent([100, 50, 20, 8, 3, 1, 0]), 0.0)
check("shoots 20 px past on a 100 start", overshoot_percent([100, 40, -20, 5, 0]), 20.0)
check("same, starting negative", overshoot_percent([-100, -40, 20, -5, 0]), 20.0)

print("\nTesting settling_time...\n")
check("empty is 0 s", settling_time([], []), 0.0)
check("settles at 0.3 s", settling_time([0, 0.1, 0.2, 0.3, 0.4], [100, 50, 20, 5, 2]), 0.3)
check("never settles = full time", settling_time([0, 0.1, 0.2, 0.3, 0.4], [100, 90, 80, 70, 60]), 0.4)
check("already small = 0 s", settling_time([0, 0.1, 0.2], [0, 0, 0]), 0.0)

print(f"\n{_passed} passed, {_failed} failed.", end=" ")
if _failed == 0:
    print("Your metrics work. Now run:  python analyze.py --sim")
else:
    print("Keep going.")
