"""my_mission.py: YOUR mission. This is where you get creative.

    python my_mission.py           <- test it in the simulator (do this a lot)
    python my_mission.py --real    <- fly it for real, in your flight slot

Pick a theme (rescue, Mars scout, delivery, anything) and build a story with the verbs.
The mission steps live in mission(drone). Keep it that way: it lets your tests in
my_tests.py run your whole mission in the simulator before you ever fly.

The verbs you can use:
    drone.takeoff()                 drone.photograph("name")
    drone.land()                    drone.celebrate()
    drone.search_for(id)            drone.flip("f")     # f b l r, off unless a facilitator enables it
    drone.search_for_any([ids])     drone.dance(["celebrate", "f"])
    drone.fly_to(id)                drone.say("text")
    drone.land_on(id)               drone.see()
    drone.visit([ids])              drone.decide(id) / drone.do(action)
"""
import argparse

from mission_toolkit import Drone


def mission(drone):
    """The mission steps. Give it a drone (sim or real) and it runs the whole thing."""
    # 1) Set the scene.
    drone.takeoff()
    drone.say("TODO: say something in character")

    # 2) TODO: find a marker and fly to it.
    #    example:
    #    target = drone.search_for_any([10, 20])
    #    if target:
    #        drone.fly_to(target)

    # 3) TODO: do something when you get there.
    #    Design decide_action() in student_code.py, then:  drone.do(drone.decide(target))
    #    Or call a verb directly: drone.photograph("evidence") / drone.celebrate() / drone.dance()

    # 4) TODO: visit more markers in an order you choose.
    #    example: drone.visit([30, 40])

    # 5) Always end by landing on base.
    drone.land_on(42)


def run(sim):
    with Drone(sim=sim, name="my_mission") as drone:
        mission(drone)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--real", action="store_true", help="Fly a real drone (default is the simulator).")
    args = parser.parse_args()
    run(sim=not args.real)
