"""check_pid.py: test your PID class in pid_exercise.py (the Part 2 stretch).

    python check_pid.py

It builds fresh PID controllers with simple gains and checks the P, I, and D parts
each behave correctly. Finish the five main functions first (python check.py), then this.
"""
from pid_exercise import PID

_passed = 0
_failed = 0


def check(name, got, want):
    global _passed, _failed
    ok = abs(got - want) < 1e-6 if isinstance(got, (int, float)) else got == want
    if ok:
        _passed += 1
    else:
        _failed += 1
    print(f"[{'PASS' if ok else 'FAIL'}] {name}   (got {got!r}, want {want!r})")


try:
    PID(0.1, 0, 0, 20).update(1.0, 0.1)
except NotImplementedError:
    print("PID.update() is not written yet. Fill it in, then run this again.")
    raise SystemExit
except Exception as exc:
    print(f"PID.update() has an error: {exc}")
    raise SystemExit

print("Testing your PID...\n")

# P part only (ki=0, kd=0): output is just kp * error, clamped.
check("P: kp * error", PID(0.1, 0, 0, 20).update(100, 0.1), 10.0)
check("P: capped at max_speed", PID(0.1, 0, 0, 20).update(500, 0.1), 20)
check("P: capped at -max_speed", PID(0.1, 0, 0, 20).update(-500, 0.1), -20)

# I part only (kp=0, kd=0): the error adds up over calls.
i_ctrl = PID(0, 1.0, 0, 100)
check("I: first step adds error*dt", i_ctrl.update(10, 0.1), 1.0)
check("I: keeps adding up", i_ctrl.update(10, 0.1), 2.0)

# D part only (kp=0, ki=0): reacts to the change in error.
d_ctrl = PID(0, 0, 1.0, 100)
check("D: zero on the first call", d_ctrl.update(10, 0.1), 0.0)
check("D: reacts to the change", d_ctrl.update(20, 0.1), 100.0)   # 1.0 * (20 - 10) / 0.1

print(f"\n{_passed} passed, {_failed} failed.", end=" ")
if _failed == 0:
    print("Your PID works. Set USE_PID = True in pid_exercise.py and try it in the simulator.")
else:
    print("Keep going.")
