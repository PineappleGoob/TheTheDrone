"""check_setup.py: is this laptop ready for the drone project?

    python check_setup.py

It checks that everything is installed and that the simulator runs. Green means ready.
You can run it any time. It does not need a drone.
"""
import sys

print(f"Python {sys.version.split()[0]}")
if not (3, 10) <= sys.version_info[:2] <= (3, 13):
    print("  [WARN] Tested on Python 3.11 and 3.12 (3.10 to 3.13 work). Yours is outside that range;")
    print("         if an install failed, install Python 3.12 from https://www.python.org/downloads/.")
print()

ready = True

for module, label in [
    ("cv2", "OpenCV"),
    ("numpy", "NumPy"),
    ("av", "av (video decoding)"),
    ("PIL", "Pillow"),
    ("matplotlib", "matplotlib"),
    ("djitellopy", "djitellopy (the drone library)"),
]:
    try:
        __import__(module)
        print(f"  [OK]       {label}")
    except Exception as exc:
        ready = False
        print(f"  [MISSING]  {label}   ->  {exc}")

# Simulator smoke test: build a drone in sim and take off / land. No drone needed.
try:
    import io
    import contextlib
    import settings
    settings.SIM_STEP_SECONDS = 0
    from mission_toolkit import Drone
    with contextlib.redirect_stdout(io.StringIO()):
        with Drone(sim=True, name="setup") as drone:
            drone.takeoff()
            drone.land()
    print("  [OK]       the simulator runs")
except Exception as exc:
    ready = False
    print(f"  [FAIL]     the simulator did not run   ->  {exc}")

print()
if ready:
    print("READY. Open DRONE_HANDBOOK.pdf and begin.")
    sys.exit(0)
else:
    print("NOT READY. Run setup_windows.bat (Windows) or  bash setup_mac_linux.sh  (Mac/Linux),")
    print("           or follow the by-hand install steps in DRONE_HANDBOOK.pdf.")
    sys.exit(1)
