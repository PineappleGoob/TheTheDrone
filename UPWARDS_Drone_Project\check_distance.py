"""check_distance.py: test distance_meters() in distance_lab.py. No drone needed.

    python check_distance.py
"""
import distance_lab

_passed = 0
_failed = 0


def check(name, got, want):
    global _passed, _failed
    if want is None:
        ok = got is None
    elif got is None:
        ok = False
    else:
        ok = abs(got - want) < 1e-6
    if ok:
        _passed += 1
    else:
        _failed += 1
    print(f"[{'PASS' if ok else 'FAIL'}] {name}   (got {got!r}, want {want!r})")


try:
    distance_lab.distance_meters(200.0)
except NotImplementedError:
    print("distance_meters() is not written yet. Fill it in, then run this again.")
    raise SystemExit
except Exception as exc:
    print(f"distance_meters() has an error: {exc}")
    raise SystemExit

# Use simple known values so the answers are easy to predict.
distance_lab.MARKER_SIZE_M = 0.20
distance_lab.FOCAL_PX = 1000.0

print("Testing distance_meters...\n")
check("side = focal, so distance = marker size", distance_lab.distance_meters(1000.0), 0.20)
check("half the pixels, twice the distance", distance_lab.distance_meters(500.0), 0.40)
check("1000 * 0.20 / 250 = 0.8 m", distance_lab.distance_meters(250.0), 0.80)
check("side = 0 gives None (cannot tell)", distance_lab.distance_meters(0), None)
check("negative side gives None", distance_lab.distance_meters(-5), None)

print(f"\n{_passed} passed, {_failed} failed.", end=" ")
if _failed == 0:
    print("It works. Calibrate FOCAL_PX (see distance_lab.py), then: python measure_distance.py")
else:
    print("Keep going.")
