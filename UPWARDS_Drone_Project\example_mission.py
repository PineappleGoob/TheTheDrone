"""example_mission.py: the worked example, a simple "scout and report" mission.

Read every line. This is the pattern you will copy and make your own.

    python example_mission.py            <- run it in the laptop simulator (no drone)
    python example_mission.py --real     <- fly it on a real drone

The mission steps live in mission(drone). It takes a drone so your tests in my_tests.py
can run the whole mission in the simulator and check what it did.
"""
import argparse

import settings
from mission_toolkit import Drone


def mission(drone):
    """The mission steps. Give it a drone (sim or real) and it runs the whole thing."""
    drone.takeoff()
    drone.flip("f")
    drone.say("Scout online. Beginning survey.")

    # DECIDE: which sample turns up first, 10 or 20?
    """found = drone.search_for_any([10, 20, 30, 40, 42])

    if found == 10:
        print("inside loop. marker 10")
        drone.fly_to(10)  
    elif found ==20:
        print("inside loop. marker 20")
        drone.fly_to(20)  
    elif found == 30:
        print("inside loop. marker 30")
        drone.fly_to(30)
    elif found == 40:
        print("inside loop. marker 40")
        drone.fly_to(40)
    elif found == 42:
        print("inside loop. marker 42")
        drone.fly_to(42)
                # LOCK ON, flown by your steer_speed()
        drone.do(drone.decide(found))     # your decide_action() picks what to do here
    else:
        drone.say("No sample in sight. Moving on.")

    # NAVIGATE: patrol the rest of the route in order
    """
    drone.visit([10, 20, 30, 40])

    # Return to base and land
    drone.land_on(settings.BASE_MARKER)
    drone.say("Survey complete.")


def run(sim):
    with Drone(sim=sim, name="example") as drone:
        mission(drone)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--real", action="store_true", help="Fly a real drone (default is the simulator).")
    args = parser.parse_args()
    run(sim=not args.real)
