"""my_tests.py: YOUR tests. Prove your code works in the simulator before you fly.

    python my_tests.py

Some tests are written for you as examples. Copy the pattern and add your own at the
bottom. Green PASS is good. The point is simple: catch your bugs on the laptop, not in
the air, so you never waste a flight slot on a mistake you could have found here.

Finish student_code.py first (run `python check.py` until it is all green). Then run this.
"""
import io
import contextlib

import settings
from student_code import clamp, centering_error, steer_speed, is_aligned, decide_action
from mission_toolkit import Drone, took_off, landed, visited, photos_taken
from my_mission import mission

ALLOWED_ACTIONS = {"photograph", "celebrate", "dance", "nothing"}

# Friendly stop if the five functions are not written yet.
for _fn, _args in [(clamp, (1, 0, 2)), (centering_error, (1, 1)), (steer_speed, (1, 1, 1)),
                   (is_aligned, (1, 1, 1, 1, 1)), (decide_action, (10,))]:
    try:
        _fn(*_args)
    except NotImplementedError:
        print(f"Finish {_fn.__name__}() in student_code.py first. Run:  python check.py")
        raise SystemExit
    except Exception:
        print(f"{_fn.__name__}() has an error. Run  python check.py  to see what to fix.")
        raise SystemExit

_passed = 0
_failed = 0


def check(name, got, want):
    """Say whether one result matches what you expected. Prints PASS or FAIL."""
    global _passed, _failed
    ok = got == want
    if ok:
        _passed += 1
    else:
        _failed += 1
    print(f"[{'PASS' if ok else 'FAIL'}] {name}   (got {got!r}, want {want!r})")


def run_mission_in_sim():
    """Run YOUR mission in the simulator (no drone) and return the list of what it did."""
    settings.SIM_STEP_SECONDS = 0          # run fast
    with contextlib.redirect_stdout(io.StringIO()):   # run quietly
        with Drone(sim=True) as drone:
            mission(drone)
            return drone.actions()


print("Running your tests...\n")

# --- Example 1: test a building block (one of your functions) ---
check("steer_speed caps at the max speed", steer_speed(9999, 0.1, 20), 20)
check("steer_speed is 0 when the error is 0", steer_speed(0, 0.1, 20), 0)

# --- Example 2: test your decision logic ---
# decide_action is your design, so this just checks it returns a real action.
# Add tests below for YOUR specific choices, like decide_action(10) == "photograph".
check("decide_action returns a real action at base 42", decide_action(42) in ALLOWED_ACTIONS, True)

# --- Example 3: test your WHOLE mission in the simulator (no drone) ---
log = run_mission_in_sim()
check("mission takes off", took_off(log), True)
check("mission lands at the end", landed(log), True)
check("mission returns to base marker 42", visited(log, 42), True)

# --- TODO: add your own tests below ---
# What else should be true before you fly? Some ideas:
#   check("mission visits sample A", visited(log, 10), True)
#   check("mission takes at least one photo", len(photos_taken(log)) >= 1, True)
#   check("is_aligned is False when far off center", is_aligned(100, 0, 0, 35, 18), False)


print(f"\n{_passed} passed, {_failed} failed.")
